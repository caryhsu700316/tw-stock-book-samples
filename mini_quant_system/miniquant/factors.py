import pandas as pd

from .config import FACTOR_WEIGHTS
from .regime import regime_bonus


def _score_trend(row: pd.Series) -> float:
    if row["close"] > row["ma5"] > row["ma20"]:
        return 9.5
    if row["close"] > row["ma20"]:
        return 6.5
    return 3.0


def _score_rsi(rsi: float) -> float:
    if pd.isna(rsi):
        return 5.0
    if 45 <= rsi <= 65:
        return 8.5
    if 35 <= rsi < 45 or 65 < rsi <= 75:
        return 6.0
    return 3.0


def _score_momentum(momentum20: float) -> float:
    if pd.isna(momentum20):
        return 5.0
    if momentum20 > 0.08:
        return 9.0
    if momentum20 > 0.02:
        return 7.0
    if momentum20 > -0.03:
        return 5.0
    return 2.5


def _score_volume(vol_ratio: float) -> float:
    if pd.isna(vol_ratio):
        return 5.0
    if 1.2 <= vol_ratio <= 2.2:
        return 8.0
    if vol_ratio > 3.0:
        return 4.0
    return 5.5


def score_candidates(day_rows: pd.DataFrame, regime: str) -> pd.DataFrame:
    stocks = day_rows[day_rows["symbol"] != "TAIEX"].copy()
    stocks["trend_score"] = stocks.apply(_score_trend, axis=1)
    stocks["rsi_score"] = stocks["rsi"].apply(_score_rsi)
    stocks["momentum_score"] = stocks["momentum20"].apply(_score_momentum)
    stocks["volume_score"] = stocks["vol_ratio"].apply(_score_volume)
    stocks["regime_score"] = regime_bonus(regime)
    stocks["score"] = (
        stocks["trend_score"] * FACTOR_WEIGHTS["trend"]
        + stocks["rsi_score"] * FACTOR_WEIGHTS["rsi"]
        + stocks["momentum_score"] * FACTOR_WEIGHTS["momentum"]
        + stocks["volume_score"] * FACTOR_WEIGHTS["volume"]
        + stocks["regime_score"] * FACTOR_WEIGHTS["regime"]
    )
    return stocks.sort_values("score", ascending=False)
