"""
第四章範例：多因子投票——把幾個指標加權成一個總分

沒有任何單一指標能一直有效，但把多個因子的「意見」綜合起來，勝算會提高。
本程式示範一個迷你版的多因子評分：對每一檔股票計算三個因子分數
（各 0~10 分），再依權重加權成總分，最後排名。

    因子一：RSI 位置     —— 不過熱也不過冷者得高分
    因子二：法人買超     —— 外資+投信買越多得分越高
    因子三：均線多頭排列 —— 站上季線且 5 日線在 20 日線之上得高分

執行方式：
    python factor_decision.py
"""

import pandas as pd

# 每個因子的權重（相加為 1.0）
WEIGHTS = {"rsi": 0.4, "inst": 0.35, "ma": 0.25}


def score_rsi(rsi: float) -> float:
    """RSI 評分：50 附近最佳，過熱（>80）或過冷（<20）扣分。"""
    if rsi >= 80 or rsi <= 20:
        return 2.0
    if 45 <= rsi <= 65:
        return 9.0
    return 6.0


def score_inst(net_buy_lots: float) -> float:
    """法人買超評分：買超越多分數越高，上限 10 分。"""
    if net_buy_lots <= 0:
        return 3.0
    # 每買超 1000 張加 1 分，最高 10 分
    return min(10.0, 5.0 + net_buy_lots / 1000.0)


def score_ma(close: float, ma5: float, ma20: float, ma60: float) -> float:
    """均線評分：多頭排列（收盤 > MA5 > MA20 > MA60）得滿分。"""
    if close > ma5 > ma20 > ma60:
        return 10.0
    if close > ma20:
        return 6.0
    return 3.0


def total_score(row: pd.Series) -> float:
    s_rsi = score_rsi(row["rsi"])
    s_inst = score_inst(row["inst_net"])
    s_ma = score_ma(row["close"], row["ma5"], row["ma20"], row["ma60"])
    return (
        s_rsi * WEIGHTS["rsi"]
        + s_inst * WEIGHTS["inst"]
        + s_ma * WEIGHTS["ma"]
    )


def main() -> None:
    # 內建假資料：股票代號、名稱、RSI、法人買超(張)、收盤、MA5、MA20、MA60
    data = [
        ("2330", "台積電", 58, 3200, 1080, 1075, 1040, 980),
        ("2454", "聯發科", 82, 800, 1300, 1310, 1280, 1250),
        ("2317", "鴻海", 49, -500, 205, 203, 208, 210),
        ("3008", "大立光", 63, 1500, 2400, 2380, 2300, 2200),
    ]
    df = pd.DataFrame(
        data,
        columns=["code", "name", "rsi", "inst_net", "close", "ma5", "ma20", "ma60"],
    )

    df["score"] = df.apply(total_score, axis=1).round(2)
    ranked = df.sort_values("score", ascending=False)

    print("=== 多因子評分排名 ===")
    print(ranked[["code", "name", "rsi", "inst_net", "score"]].to_string(index=False))
    print(f"\n今日首選：{ranked.iloc[0]['name']}（總分 {ranked.iloc[0]['score']}）")


if __name__ == "__main__":
    main()
