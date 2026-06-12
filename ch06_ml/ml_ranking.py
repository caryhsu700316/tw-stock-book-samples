"""
第六章範例：最簡單的機器學習——用隨機森林排序股票

機器學習在選股上的價值，不是「精準預測明天漲跌」（做不到），
而是「從一堆股票裡，排出最有機會的那幾檔」。本程式示範一個迷你版的
排名式選股：用幾個技術特徵訓練隨機森林，預測每檔股票「上漲的機率」，
再依機率排名。

    特徵：RSI、20 日動能、法人買超、量比
    標籤：未來是否上漲（1 = 漲，0 = 跌）—— 範例用假資料示範

執行方式：
    python ml_ranking.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def make_training_data(n: int = 500, seed: int = 7):
    """產生假的訓練資料：特徵與「未來是否上漲」的標籤。

    這裡刻意讓 RSI 適中、動能為正、法人買超的股票比較容易上漲，
    模型應該要能學到這個關係。
    """
    rng = np.random.default_rng(seed)
    rsi = rng.uniform(10, 90, n)
    momentum = rng.normal(0, 0.05, n)
    inst = rng.normal(0, 1500, n)
    vol_ratio = rng.uniform(0.5, 3.0, n)

    # 用一個隱藏規則決定標籤，再加上雜訊
    signal = (
        (np.abs(rsi - 55) < 15).astype(float)
        + (momentum > 0).astype(float)
        + (inst > 0).astype(float)
    )
    prob = 1 / (1 + np.exp(-(signal - 1.5)))
    label = (rng.uniform(0, 1, n) < prob).astype(int)

    X = pd.DataFrame(
        {"rsi": rsi, "momentum": momentum, "inst": inst, "vol_ratio": vol_ratio}
    )
    return X, label


def main() -> None:
    # 1. 準備訓練資料並訓練模型
    X_train, y_train = make_training_data()
    model = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=7)
    model.fit(X_train, y_train)

    # 2. 今天要評估的候選股票（假資料）
    today = pd.DataFrame(
        {
            "name": ["台積電", "聯發科", "鴻海", "大立光", "廣達"],
            "rsi": [58, 82, 49, 63, 41],
            "momentum": [0.03, 0.06, -0.02, 0.04, 0.01],
            "inst": [3200, 800, -500, 1500, 200],
            "vol_ratio": [1.8, 2.5, 0.9, 1.6, 1.1],
        }
    )

    # 3. 預測上漲機率，並排名
    features = ["rsi", "momentum", "inst", "vol_ratio"]
    today["up_prob"] = model.predict_proba(today[features])[:, 1].round(3)
    ranked = today.sort_values("up_prob", ascending=False)

    print("=== ML 排名式選股（上漲機率） ===")
    print(ranked[["name", "up_prob"]].to_string(index=False))
    print(f"\n模型最看好：{ranked.iloc[0]['name']}（機率 {ranked.iloc[0]['up_prob']}）")


if __name__ == "__main__":
    main()
