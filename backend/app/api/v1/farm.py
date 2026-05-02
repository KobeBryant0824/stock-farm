import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.farm import User, Farm, FarmPlot, HarvestRecord
from app.redis_client import get_redis
from app.services.akshare_service import AKShareService
from app.services.growth_engine import calculate_plant_status, get_stage_index

router = APIRouter(prefix="/farm", tags=["farm"])

TOTAL_PLOTS = 6


# ---------- Schemas ----------

class PlantSeedRequest(BaseModel):
    stock_code: str
    stock_name: str
    slot_index: int


# ---------- Helpers ----------

def _get_or_create_user(device_id: str, db: Session) -> User:
    user = db.query(User).filter(User.id == device_id).first()
    if not user:
        user = User(id=device_id)
        farm = Farm(id=str(uuid.uuid4()), user_id=device_id)
        plots = [
            FarmPlot(id=str(uuid.uuid4()), farm_id=farm.id, slot_index=i)
            for i in range(TOTAL_PLOTS)
        ]
        db.add(user)
        db.add(farm)
        db.bulk_save_objects(plots)
        db.commit()
        db.refresh(user)
    return user


def _enrich_plot(plot: FarmPlot, quotes: dict) -> dict:
    """把数据库地块 + 实时行情 → 前端需要的完整状态"""
    if plot.status == "empty" or not plot.stock_code:
        return {"slot_index": plot.slot_index, "status": "empty"}

    quote = quotes.get(plot.stock_code)
    current_price = quote["price"] if quote else plot.buy_price  # 无行情时用买入价（涨幅=0）

    growth = calculate_plant_status(current_price, plot.buy_price)

    return {
        "slot_index": plot.slot_index,
        "plot_id": plot.id,
        "stock_code": plot.stock_code,
        "stock_name": plot.stock_name,
        "buy_price": plot.buy_price,
        "current_price": current_price,
        "return_pct": round(growth.return_pct, 2),
        "status": growth.status,
        "stage_index": get_stage_index(growth.status),  # 0-5，前端动画用
        "is_harvestable": growth.is_harvestable,
        "planted_at": plot.planted_at.isoformat() if plot.planted_at else None,
    }


# ---------- Routes ----------

@router.get("/{device_id}")
def get_farm(device_id: str, db: Session = Depends(get_db)):
    """获取农场全状态（含实时行情驱动的植物状态）"""
    user = _get_or_create_user(device_id, db)
    farm = user.farm
    plots = farm.plots

    # 批量拉行情
    active_codes = [p.stock_code for p in plots if p.stock_code]
    quotes = {}
    if active_codes:
        try:
            svc = AKShareService(get_redis())
            quotes = svc.get_batch_quotes(active_codes)
        except Exception:
            pass  # 非交易时段或网络问题，用买入价兜底

    enriched = [_enrich_plot(p, quotes) for p in plots]
    return {"farm_id": farm.id, "name": farm.name, "plots": enriched}


@router.post("/{device_id}/plant")
def plant_seed(device_id: str, req: PlantSeedRequest, db: Session = Depends(get_db)):
    """把股票种到指定地块"""
    user = _get_or_create_user(device_id, db)
    plot = (
        db.query(FarmPlot)
        .filter(
            FarmPlot.farm_id == user.farm.id,
            FarmPlot.slot_index == req.slot_index,
        )
        .first()
    )
    if not plot:
        raise HTTPException(status_code=404, detail="地块不存在")
    if plot.status != "empty":
        raise HTTPException(status_code=400, detail="该地块已有植物")

    # 拉当前价作为买入价；实时行情失败则降级到历史收盘价
    buy_price = None
    svc = AKShareService(get_redis())
    try:
        quote = svc.get_realtime_quote(req.stock_code)
        price = quote.get("price", 0)
        if price and float(price) > 0:
            buy_price = float(price)
    except Exception:
        pass

    if not buy_price:
        try:
            import akshare as ak
            df = ak.stock_zh_a_hist(symbol=req.stock_code, period="daily", adjust="qfq")
            if not df.empty:
                buy_price = float(df.iloc[-1]["收盘"])
        except Exception:
            pass

    if not buy_price:
        raise HTTPException(status_code=503, detail="暂时无法获取该股票价格，请稍后重试")

    plot.stock_code = req.stock_code
    plot.stock_name = req.stock_name
    plot.buy_price = buy_price
    plot.planted_at = datetime.utcnow()
    plot.status = "seed"
    db.commit()

    return {"message": "种植成功", "buy_price": buy_price}


@router.post("/{device_id}/harvest/{plot_id}")
def harvest(device_id: str, plot_id: str, db: Session = Depends(get_db)):
    """收获：涨幅≥20%才能收"""
    user = _get_or_create_user(device_id, db)
    plot = db.query(FarmPlot).filter(FarmPlot.id == plot_id, FarmPlot.farm_id == user.farm.id).first()
    if not plot or not plot.stock_code:
        raise HTTPException(status_code=404, detail="地块不存在")

    svc = AKShareService(get_redis())
    quote = svc.get_realtime_quote(plot.stock_code)
    growth = calculate_plant_status(quote["price"], plot.buy_price)

    if not growth.is_harvestable:
        raise HTTPException(
            status_code=400,
            detail=f"涨幅仅 {growth.return_pct:.1f}%，需要达到 20% 才能收获",
        )

    # 记录收获
    record = HarvestRecord(
        id=str(uuid.uuid4()),
        user_id=device_id,
        stock_code=plot.stock_code,
        stock_name=plot.stock_name,
        buy_price=plot.buy_price,
        harvest_price=quote["price"],
        total_return_pct=growth.return_pct,
        planted_at=plot.planted_at,
    )
    db.add(record)

    # 清空地块
    plot.stock_code = None
    plot.stock_name = None
    plot.buy_price = None
    plot.planted_at = None
    plot.status = "empty"
    plot.is_harvestable = False
    db.commit()

    return {
        "message": "收获成功！",
        "return_pct": round(growth.return_pct, 2),
        "harvest_price": quote["price"],
    }


@router.delete("/{device_id}/remove/{plot_id}")
def remove_plant(device_id: str, plot_id: str, db: Session = Depends(get_db)):
    """铲掉植物（无论涨跌，强制清空地块）"""
    user = _get_or_create_user(device_id, db)
    plot = db.query(FarmPlot).filter(FarmPlot.id == plot_id, FarmPlot.farm_id == user.farm.id).first()
    if not plot:
        raise HTTPException(status_code=404, detail="地块不存在")

    plot.stock_code = None
    plot.stock_name = None
    plot.buy_price = None
    plot.planted_at = None
    plot.status = "empty"
    plot.is_harvestable = False
    db.commit()
    return {"message": "已铲除"}
