import requests
from fastapi import APIRouter, HTTPException
from app.redis_client import get_redis
from app.services.akshare_service import AKShareService

router = APIRouter(prefix="/stocks", tags=["stocks"])


def _svc() -> AKShareService:
    return AKShareService(get_redis())


def _sina_search(keyword: str) -> list[dict]:
    """
    新浪财经实时搜索建议接口，毫秒级返回，无需预加载。
    支持股票代码和名称搜索，如 "平安" 或 "000001"。
    """
    url = f"https://suggest3.sinajs.cn/suggest/type=11,12&key={keyword}&name=suggestdata"
    try:
        r = requests.get(
            url,
            headers={"Referer": "https://finance.sina.com.cn"},
            timeout=5,
        )
        r.encoding = "gbk"
        text = r.text.strip()
        # 格式: var suggestdata="平安银行,11,000001,,...;中国平安,11,601318,,..."
        if not text or '"' not in text:
            return []
        inner = text.split('"')[1]
        if not inner:
            return []
        results = []
        seen = set()
        for item in inner.split(";"):
            parts = item.split(",")
            if len(parts) < 5 or parts[1] not in ("11", "12"):
                continue
            code = parts[2]
            symbol = parts[3]  # 如 "sh600519" 或 "sz000001"
            name = parts[4] if parts[4] else parts[0]

            # 根据代码首位判断正确交易所，过滤掉代码相同但交易所不对的（如 sh000001=指数 vs sz000001=股票）
            if code.startswith("6") and not symbol.startswith("sh"):
                continue
            if (code.startswith("0") or code.startswith("3")) and not symbol.startswith("sz"):
                continue

            if code in seen:
                continue
            seen.add(code)
            results.append({"code": code, "name": name})
        return results[:20]
    except Exception:
        return []


@router.get("/search")
def search_stocks(q: str):
    """搜索A股，按代码或名称搜索"""
    q = q.strip()
    if not q:
        raise HTTPException(status_code=400, detail="请输入搜索关键词")

    results = _sina_search(q)

    # 新浪接口失败时降级用本地缓存
    if not results:
        try:
            results = _svc().search_stocks(q)
        except Exception:
            results = []

    return {"results": results}


@router.get("/quote/{stock_code}")
def get_quote(stock_code: str):
    """获取单只股票实时行情"""
    try:
        return _svc().get_realtime_quote(stock_code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
