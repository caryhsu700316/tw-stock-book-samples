import numpy as np
import pandas as pd


def _rsi(close: pd.Series, window: int = 14) -> pd.Series:
    diff = close.diff()
    gain = diff.clip(lower=0).rolling(window).mean()
    loss = (-diff.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def add_indicators(prices: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, group in prices.groupby("symbol"):
        df = group.sort_values("trade_date").copy()
        df["ma5"] = df["close"].rolling(5).mean()
        df["ma20"] = df["close"].rolling(20).mean()
        df["rsi"] = _rsi(df["close"])
        df["momentum20"] = df["close"].pct_change(20)
        df["vol_ma20"] = df["volume"].rolling(20).mean()
        df["vol_ratio"] = df["volume"] / df["vol_ma20"]
        frames.append(df)
    return pd.concat(frames, ignore_index=True)
