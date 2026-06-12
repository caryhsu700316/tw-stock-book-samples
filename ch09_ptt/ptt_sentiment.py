"""
第九章範例：PTT 社群分析——統計看多看空的情緒

新聞標題和網路討論裡，藏著散戶的情緒，而散戶的情緒常常是反向指標。
本程式示範如何抓取 PTT 股票板（Stock）的文章標題，用一份簡單的
看多／看空關鍵字字典，統計當前版面的情緒傾向。

    情緒分數 = （看多標題數 - 看空標題數） / 總標題數

執行方式：
    python ptt_sentiment.py

注意：PTT 網頁版可能調整結構或加上流量限制，若抓取失敗，
程式會改用內建的範例標題示範計算邏輯。
"""

import re
import time
import requests

PTT_STOCK_URL = "https://www.ptt.cc/bbs/Stock/index.html"

# 簡易看多／看空關鍵字字典（實務上會用更完整的詞庫或 NLP 模型）
BULLISH = ["漲停", "噴出", "多頭", "創新高", "利多", "大漲", "起飛", "突破"]
BEARISH = ["跌停", "崩跌", "空頭", "創新低", "利空", "大跌", "套牢", "認賠"]


def fetch_titles() -> list[str]:
    """抓取 PTT 股票板首頁的文章標題。失敗時回傳空清單。"""
    headers = {"User-Agent": "Mozilla/5.0 (book-sample/1.0)"}
    # over18=1 用來通過 PTT 的年齡確認
    cookies = {"over18": "1"}
    try:
        resp = requests.get(PTT_STOCK_URL, headers=headers, cookies=cookies, timeout=15)
        resp.raise_for_status()
    except Exception as exc:  # 網路或結構問題時退回範例資料
        print(f"（抓取失敗，改用範例資料示範：{exc}）")
        return []

    # 用簡單的正規表達式取出標題（避免額外依賴解析套件）
    titles = re.findall(r'<div class="title">\s*<a[^>]*>(.*?)</a>', resp.text, re.S)
    return [t.strip() for t in titles]


def classify(title: str) -> int:
    """判斷單一標題情緒：+1 看多、-1 看空、0 中性。"""
    if any(word in title for word in BULLISH):
        return 1
    if any(word in title for word in BEARISH):
        return -1
    return 0


def main() -> None:
    titles = fetch_titles()
    time.sleep(2)  # 禮貌性延遲

    if not titles:
        # 退回範例資料，仍能示範計算邏輯
        titles = [
            "[標的] 台積電多頭噴出，目標價上看",
            "[請益] 手上這檔套牢了怎麼辦",
            "[新聞] 某某產業利多消息",
            "[閒聊] 今天大盤盤整",
            "[標的] 這檔跌停鎖死，空頭氣勢強",
        ]

    bull = sum(1 for t in titles if classify(t) > 0)
    bear = sum(1 for t in titles if classify(t) < 0)
    total = len(titles)
    score = (bull - bear) / total if total else 0.0

    print(f"共分析 {total} 則標題")
    print(f"看多：{bull} 則，看空：{bear} 則")
    print(f"情緒分數：{score:+.2f}（>0 偏多、<0 偏空）")

    if score > 0.2:
        print("提醒：散戶情緒偏熱，留意反向風險")
    elif score < -0.2:
        print("提醒：散戶情緒偏冷，可能是相對低點")
    else:
        print("情緒中性")


if __name__ == "__main__":
    main()
