"""
第十章範例：用 LINE Messaging API 把選股結果推到手機

系統不能只活在命令列裡。本程式示範用 LINE Messaging API 的
「主動推播（Push Message）」功能，把今日選股結果送到你的手機。

事前準備（詳見第十章內文）：
    1. 到 LINE Developers 建立一個 Messaging API channel
    2. 取得 Channel access token（長期）
    3. 取得你自己的 User ID（用 webhook 或 LINE Official Account Manager）

執行方式：
    set LINE_TOKEN=你的_channel_access_token        （Windows）
    set LINE_USER_ID=你的_user_id
    python line_push.py

安全提醒：絕對不要把 token 寫死在程式碼裡或上傳到 GitHub，
請改用環境變數或設定檔（並把設定檔加入 .gitignore）。
"""

import os
import requests

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


def push_message(token: str, user_id: str, text: str) -> None:
    """透過 LINE Messaging API 推送一則文字訊息給指定使用者。"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}],
    }
    resp = requests.post(LINE_PUSH_URL, headers=headers, json=body, timeout=15)
    resp.raise_for_status()
    print("已送出 LINE 訊息")


def build_report() -> str:
    """組出一則選股報告文字（這裡用假資料示範）。"""
    picks = [
        ("2330", "台積電", 8.5),
        ("2454", "聯發科", 8.2),
        ("3008", "大立光", 7.6),
    ]
    lines = ["📊 今日選股報告", ""]
    for i, (code, name, score) in enumerate(picks, start=1):
        lines.append(f"{i}. {code} {name}  Score: {score}")
    lines.append("")
    lines.append("⚠ 本訊息僅供學習，非投資建議")
    return "\n".join(lines)


def main() -> None:
    token = os.environ.get("LINE_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")

    report = build_report()

    if not token or not user_id:
        # 沒有設定金鑰時，僅在終端機印出，方便先看到組好的內容
        print("（未設定 LINE_TOKEN / LINE_USER_ID，以下為將送出的內容）\n")
        print(report)
        return

    push_message(token, user_id, report)


if __name__ == "__main__":
    main()
