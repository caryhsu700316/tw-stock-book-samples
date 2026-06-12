"""
第五章範例：判斷市場環境——牛市、盤整還是熊市

同一套策略，在多頭大賺、在空頭可能大虧。所以系統要先看懂「現在是什麼天氣」。
本程式示範一個迷你版的市場環境（Regime）判斷：用大盤指數的
均線位置與近期動能，把市場分成三種狀態。

    BULL（多頭）  ：指數站上 60 日線、且 20 日線在 60 日線之上
    BEAR（空頭）  ：指數跌破 60 日線、且 20 日線在 60 日線之下
    NEUTRAL（盤整）：其餘情況

執行方式：
    python market_regime.py
"""

import numpy as np
import pandas as pd


def judge_regime(close: pd.Series) -> str:
    """根據收盤價序列判斷目前市場環境。

    參數 close 需至少包含 60 個交易日的大盤收盤價。
    """
    ma20 = close.rolling(20).mean().iloc[-1]
    ma60 = close.rolling(60).mean().iloc[-1]
    last = close.iloc[-1]

    # 近 20 日報酬率，作為動能參考
    momentum = close.iloc[-1] / close.iloc[-20] - 1

    if last > ma60 and ma20 > ma60 and momentum > 0:
        return "BULL"
    if last < ma60 and ma20 < ma60 and momentum < 0:
        return "BEAR"
    return "NEUTRAL"


# 不同環境下，系統採用的策略參數
REGIME_CONFIG = {
    "BULL": {"max_positions": 8, "buy_score_min": 6.0, "note": "積極：多持股、放寬買入門檻"},
    "NEUTRAL": {"max_positions": 6, "buy_score_min": 6.5, "note": "中性：標準配置"},
    "BEAR": {"max_positions": 3, "buy_score_min": 7.5, "note": "保守：減碼、提高買入門檻、加買避險工具"},
}


def main() -> None:
    # 用隨機漫步產生一段假的大盤走勢，方便示範
    rng = np.random.default_rng(42)
    # 製造一段先漲後跌的走勢
    up = np.cumsum(rng.normal(0.3, 1.0, 60)) + 100
    down = up[-1] + np.cumsum(rng.normal(-0.5, 1.0, 30))
    close = pd.Series(np.concatenate([up, down]))

    regime = judge_regime(close)
    config = REGIME_CONFIG[regime]

    print(f"目前大盤收盤：{close.iloc[-1]:.1f}")
    print(f"判斷的市場環境：{regime}")
    print(f"對應策略：{config['note']}")
    print(f"  最大持股檔數：{config['max_positions']}")
    print(f"  買入分數門檻：{config['buy_score_min']}")


if __name__ == "__main__":
    main()
