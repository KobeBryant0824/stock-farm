from dataclasses import dataclass


# 植物状态，从低到高
PLANT_STAGES = ["seed", "sprout", "seedling", "sapling", "tree", "full_tree"]

# 涨幅阈值 → 对应植物状态
# 规则：被套(return_pct < 0) → seed(不发芽)
#       涨幅越高，植物越大
GROWTH_THRESHOLDS = [
    (20.0, "full_tree"),   # 涨幅 ≥ 20% → 参天大树（可收获）
    (10.0, "tree"),        # 涨幅 ≥ 10% → 大树
    (5.0,  "sapling"),     # 涨幅 ≥  5% → 树苗
    (2.0,  "seedling"),    # 涨幅 ≥  2% → 小树苗
    (0.0,  "sprout"),      # 涨幅 ≥  0% → 发芽（刚解套）
    # 其余全是 seed（被套，不发芽）
]


@dataclass
class GrowthResult:
    status: str        # 植物状态
    return_pct: float  # 相对买入价的涨幅
    is_harvestable: bool


def calculate_plant_status(current_price: float, buy_price: float) -> GrowthResult:
    """
    核心逻辑：当前价格 vs 买入价 → 植物状态
    被套不发芽，盈利越多树越大
    """
    if buy_price <= 0:
        return GrowthResult(status="seed", return_pct=0.0, is_harvestable=False)

    return_pct = (current_price - buy_price) / buy_price * 100

    if return_pct < 0:
        return GrowthResult(status="seed", return_pct=return_pct, is_harvestable=False)

    for threshold, status in GROWTH_THRESHOLDS:
        if return_pct >= threshold:
            return GrowthResult(
                status=status,
                return_pct=return_pct,
                is_harvestable=(status == "full_tree"),
            )

    return GrowthResult(status="seed", return_pct=return_pct, is_harvestable=False)


def get_stage_index(status: str) -> int:
    """返回0-5的生长阶段数字，供前端驱动动画进度"""
    try:
        return PLANT_STAGES.index(status)
    except ValueError:
        return 0
