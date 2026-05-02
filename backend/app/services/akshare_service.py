import json
import requests
import akshare as ak
from datetime import datetime


def _market_prefix(code: str) -> str:
    """根据股票代码判断交易所前缀（新浪财经格式）"""
    if code.startswith("6"):
        return f"sh{code}"
    return f"sz{code}"


def _sina_quote(code: str) -> dict | None:
    """
    从新浪财经接口拉单只股票实时行情。
    返回格式: {code, name, price, change_pct, timestamp}
    非交易时间返回昨收价，change_pct=0。
    """
    symbol = _market_prefix(code)
    try:
        r = requests.get(
            f"https://hq.sinajs.cn/list={symbol}",
            headers={"Referer": "https://finance.sina.com.cn"},
            timeout=8,
        )
        r.encoding = "gbk"
        content = r.text.strip()
        # 格式: var hq_str_sh600519="贵州茅台,开,昨收,现价,最高,最低,..."
        if '""' in content or not content:
            return None
        inner = content.split('"')[1]
        parts = inner.split(",")
        if len(parts) < 4:
            return None
        name = parts[0]
        yesterday_close = float(parts[2]) if parts[2] else 0
        current_price = float(parts[3]) if parts[3] else 0
        change_pct = (
            (current_price - yesterday_close) / yesterday_close * 100
            if yesterday_close > 0
            else 0.0
        )
        return {
            "code": code,
            "name": name,
            "price": current_price,
            "change_pct": round(change_pct, 2),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception:
        return None


class AKShareService:
    def __init__(self, cache):
        self.cache = cache          # 兼容 Redis 或内存缓存
        self.QUOTE_TTL = 300
        self.STOCK_LIST_TTL = 86400

    def get_realtime_quote(self, stock_code: str) -> dict:
        """获取单只股票实时行情，优先新浪财经，失败则 AKShare 历史收盘价兜底"""
        cache_key = f"quote:{stock_code}"
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # 1. 新浪财经（主）
        data = _sina_quote(stock_code)

        # 2. AKShare 历史收盘价（兜底）
        if not data or data["price"] <= 0:
            try:
                df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")
                if not df.empty:
                    last = df.iloc[-1]
                    data = {
                        "code": stock_code,
                        "name": stock_code,
                        "price": float(last["收盘"]),
                        "change_pct": float(last.get("涨跌幅", 0)),
                        "timestamp": datetime.now().isoformat(),
                    }
            except Exception:
                pass

        if not data or data["price"] <= 0:
            raise ValueError(f"无法获取股票 {stock_code} 的价格")

        self.cache.setex(cache_key, self.QUOTE_TTL, json.dumps(data, ensure_ascii=False))
        return data

    def get_batch_quotes(self, stock_codes: list[str]) -> dict[str, dict]:
        """批量获取行情（新浪财经一次请求多只）"""
        if not stock_codes:
            return {}

        # 先查缓存
        result = {}
        missing = []
        for code in stock_codes:
            cached = self.cache.get(f"quote:{code}")
            if cached:
                result[code] = json.loads(cached)
            else:
                missing.append(code)

        if not missing:
            return result

        # 批量请求新浪财经
        symbols = ",".join(_market_prefix(c) for c in missing)
        try:
            r = requests.get(
                f"https://hq.sinajs.cn/list={symbols}",
                headers={"Referer": "https://finance.sina.com.cn"},
                timeout=10,
            )
            r.encoding = "gbk"
            for line in r.text.strip().split("\n"):
                line = line.strip()
                if not line or '""' in line:
                    continue
                # var hq_str_sz000001="平安银行,..."
                sym = line.split("=")[0].replace("var hq_str_", "").strip()
                code = sym[2:]  # 去掉 sh/sz 前缀
                inner = line.split('"')[1]
                parts = inner.split(",")
                if len(parts) < 4:
                    continue
                yesterday_close = float(parts[2]) if parts[2] else 0
                current_price = float(parts[3]) if parts[3] else 0
                change_pct = (
                    (current_price - yesterday_close) / yesterday_close * 100
                    if yesterday_close > 0 else 0.0
                )
                data = {
                    "code": code,
                    "name": parts[0],
                    "price": current_price,
                    "change_pct": round(change_pct, 2),
                    "timestamp": datetime.now().isoformat(),
                }
                result[code] = data
                self.cache.setex(f"quote:{code}", self.QUOTE_TTL, json.dumps(data, ensure_ascii=False))
        except Exception:
            pass

        return result

    def search_stocks(self, keyword: str) -> list[dict]:
        """按代码或名称模糊搜索A股"""
        cache_key = "stock:list"
        cached = self.cache.get(cache_key)

        if cached:
            stock_list = json.loads(cached)
        else:
            df = ak.stock_info_a_code_name()
            stock_list = df[["code", "name"]].to_dict("records")
            self.cache.setex(cache_key, self.STOCK_LIST_TTL, json.dumps(stock_list, ensure_ascii=False))

        kw = keyword.strip()
        results = [s for s in stock_list if kw in s["code"] or kw in s["name"]]
        return results[:20]
