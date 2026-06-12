"""
第二章範例：用爬蟲從台灣證券交易所抓股票日成交資料

這是全書最基礎的一個範例：沒有資料，後面的指標、因子、機器學習都無從談起。
本程式示範如何呼叫台灣證券交易所（TWSE）的公開 API，抓取單一股票
某個月份的每日成交資訊（開高低收與成交量），並整理成乾淨的表格。

執行方式：
    python fetch_stock.py

預設抓取台積電（2330）當月資料。可在最下方修改股票代號與月份。
"""

import time
import requests
import pandas as pd

# TWSE「個股日成交資訊」公開 API
TWSE_URL = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"


def fetch_one_month(stock_code: str, year_month: str) -> pd.DataFrame:
    """抓取單一股票、單一月份的日成交資料。

    參數：
        stock_code: 股票代號，例如 "2330"
        year_month: 西元年月，格式 "YYYYMM01"，例如 "20260601"
    回傳：
        整理後的 DataFrame，欄位為日期、開、高、低、收、量
    """
    params = {"response": "json", "date": year_month, "stockNo": stock_code}

    # 加上 User-Agent，避免被當成可疑流量擋掉
    headers = {"User-Agent": "Mozilla/5.0 (book-sample/1.0)"}
    resp = requests.get(TWSE_URL, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    if payload.get("stat") != "OK":
        # API 沒有資料時（例如未開市的月份）會回傳非 OK 狀態
        raise RuntimeError(f"TWSE 回傳非 OK：{payload.get('stat')}")

    # data 是一個二維陣列，每一列是一天的資料
    # 欄位順序：日期, 成交股數, 成交金額, 開盤, 最高, 最低, 收盤, 漲跌價差, 成交筆數
    rows = payload["data"]
    df = pd.DataFrame(rows, columns=payload["fields"])

    # 清理：把帶有逗號的數字字串轉成數值
    def to_number(series: pd.Series) -> pd.Series:
        return pd.to_numeric(series.str.replace(",", "", regex=False), errors="coerce")

    clean = pd.DataFrame(
        {
            "date": df["日期"],  # 民國年格式，這裡保留原樣示範
            "open": to_number(df["開盤價"]),
            "high": to_number(df["最高價"]),
            "low": to_number(df["最低價"]),
            "close": to_number(df["收盤價"]),
            "volume": to_number(df["成交股數"]),
        }
    )
    clean["stock_code"] = stock_code
    return clean


def main() -> None:
    stock_code = "2330"      # 台積電
    year_month = "20260601"  # 2026 年 6 月

    print(f"抓取 {stock_code} 在 {year_month[:6]} 的日成交資料……")
    df = fetch_one_month(stock_code, year_month)

    # 禮貌性延遲：避免短時間內大量請求造成對方伺服器負擔
    time.sleep(3)

    print(f"共取得 {len(df)} 筆資料\n")
    print(df.tail(10).to_string(index=False))

    # 存成 CSV，之後就能匯入資料庫或用來算技術指標
    out_path = f"{stock_code}_{year_month[:6]}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\n已存檔：{out_path}")


if __name__ == "__main__":
    main()
