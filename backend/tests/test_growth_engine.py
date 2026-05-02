import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.growth_engine import calculate_plant_status


def test_被套不发芽():
    r = calculate_plant_status(current_price=9.0, buy_price=10.0)
    assert r.status == "seed"
    assert r.return_pct < 0
    assert not r.is_harvestable


def test_刚解套发芽():
    r = calculate_plant_status(current_price=10.05, buy_price=10.0)
    assert r.status == "sprout"
    assert not r.is_harvestable


def test_涨2percent小苗():
    # 用 10.21 确保涨幅明确超过 2%，避免浮点边界问题
    r = calculate_plant_status(current_price=10.21, buy_price=10.0)
    assert r.status == "seedling"


def test_涨5percent树苗():
    r = calculate_plant_status(current_price=10.5, buy_price=10.0)
    assert r.status == "sapling"


def test_涨10percent大树():
    r = calculate_plant_status(current_price=11.0, buy_price=10.0)
    assert r.status == "tree"


def test_涨20percent参天大树可收获():
    r = calculate_plant_status(current_price=12.0, buy_price=10.0)
    assert r.status == "full_tree"
    assert r.is_harvestable


def test_跌停仍是种子():
    r = calculate_plant_status(current_price=9.01, buy_price=10.0)
    assert r.status == "seed"
    assert not r.is_harvestable


def test_buy_price为零不崩溃():
    r = calculate_plant_status(current_price=10.0, buy_price=0)
    assert r.status == "seed"
