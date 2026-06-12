"""
第三章範例：讓程式看懂 K 線——辨識三種經典型態

K 線型態是把「開、高、低、收」四個價格的相對關係，翻譯成有意義的訊號。
本程式示範如何用純計算辨識三種常見型態：
    1. 十字星（Doji）       ：開盤與收盤幾乎相同，代表多空僵持
    2. 錘子（Hammer）       ：下影線很長、實體在上方，常出現在低點，可能止跌
    3. 多頭吞噬（Bullish Engulfing）：今天的紅 K 完全包住昨天的黑 K，買盤轉強

執行方式：
    python detect_kline.py

範例使用內建的假資料，方便你直接看到結果；實務上會改成讀取
第二章抓下來的股價資料。
"""

import pandas as pd


def detect_doji(o, h, l, c) -> bool:
    """十字星：實體很小（開收接近），但有上下影線。"""
    body = abs(c - o)
    candle_range = h - l
    if candle_range == 0:
        return False
    # 實體佔整根 K 線不到 10%，視為十字星
    return body / candle_range < 0.1


def detect_hammer(o, h, l, c) -> bool:
    """錘子：下影線長（至少是實體的兩倍），上影線短，實體在上半部。"""
    body = abs(c - o)
    lower_shadow = min(o, c) - l
    upper_shadow = h - max(o, c)
    if body == 0:
        return False
    return lower_shadow >= 2 * body and upper_shadow <= body


def detect_bullish_engulfing(prev, curr) -> bool:
    """多頭吞噬：前一天收黑、今天收紅，且今天實體完全包住前一天實體。"""
    prev_black = prev["close"] < prev["open"]
    curr_red = curr["close"] > curr["open"]
    engulf = curr["open"] <= prev["close"] and curr["close"] >= prev["open"]
    return prev_black and curr_red and engulf


def scan(df: pd.DataFrame) -> pd.DataFrame:
    """逐日掃描，標記每一天命中的型態。"""
    results = []
    for i in range(len(df)):
        row = df.iloc[i]
        patterns = []
        if detect_doji(row["open"], row["high"], row["low"], row["close"]):
            patterns.append("十字星")
        if detect_hammer(row["open"], row["high"], row["low"], row["close"]):
            patterns.append("錘子")
        if i > 0 and detect_bullish_engulfing(df.iloc[i - 1], row):
            patterns.append("多頭吞噬")
        results.append("、".join(patterns) if patterns else "—")
    out = df.copy()
    out["pattern"] = results
    return out


def main() -> None:
    # 內建假資料：日期、開、高、低、收
    data = [
        ("06-03", 100.0, 102.0, 99.5, 101.5),
        ("06-04", 101.5, 101.8, 95.0, 96.0),   # 收黑
        ("06-05", 95.5, 103.0, 95.0, 102.5),   # 紅 K 包住前一天 → 多頭吞噬
        ("06-06", 102.5, 103.0, 102.4, 102.55), # 開收幾乎相同 → 十字星
        ("06-07", 98.0, 99.5, 93.0, 99.0),       # 長下影線、短上影線 → 錘子
    ]
    df = pd.DataFrame(data, columns=["date", "open", "high", "low", "close"])

    result = scan(df)
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
