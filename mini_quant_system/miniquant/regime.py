import pandas as pd


def detect_regime(indicators: pd.DataFrame, trade_date: str) -> str:
    index_row = indicators[
        (indicators["symbol"] == "TAIEX") & (indicators["trade_date"] == trade_date)
    ]
    if index_row.empty:
        return "NEUTRAL"

    row = index_row.iloc[0]
    if pd.isna(row["ma20"]) or pd.isna(row["momentum20"]):
        return "NEUTRAL"
    if row["close"] > row["ma20"] and row["momentum20"] > 0.03:
        return "BULL"
    if row["close"] < row["ma20"] and row["momentum20"] < -0.03:
        return "BEAR"
    return "NEUTRAL"


def regime_bonus(regime: str) -> float:
    return {"BULL": 8.0, "NEUTRAL": 5.5, "BEAR": 2.0}.get(regime, 5.0)
