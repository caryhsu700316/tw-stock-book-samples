# 實作篇：最小量化選股系統

這個範例把書中各章的核心觀念串成一套可以在本機執行的小型系統：

1. 產生範例股價資料並寫入 SQL Server Express
2. 計算 RSI、均線、動能與量比
3. 依五個因子產生股票排名
4. 判斷市場環境是 BULL、NEUTRAL 或 BEAR
5. 套用停損、部位大小與現金限制
6. 執行一個簡化回測
7. 輸出 CSV 與 HTML 報告

這不是可以直接拿去交易的系統，而是讓你看懂「一套量化系統最小需要哪些零件」。

## 執行方式

請先在 `docs/book1/sample` 安裝共用套件：

```bash
pip install -r requirements.txt
```

MiniQuant 預設連線到 `localhost\SQLEXPRESS`，並使用 `MiniQuantDemo` 資料庫。若你的 SQL Server Express instance 名稱不同，可以先設定環境變數：

```powershell
$env:MINIQUANT_SQL_SERVER = "localhost\SQLEXPRESS"
$env:MINIQUANT_SQL_DATABASE = "MiniQuantDemo"
```

如果你已安裝 SQL Server Express 但服務尚未啟動，請在 Windows 服務管理工具中啟動 `SQL Server (SQLEXPRESS)`，或在有權限的 PowerShell 中執行：

```powershell
Start-Service -Name 'MSSQL$SQLEXPRESS'
```

然後執行：

```bash
cd mini_quant_system
python run_demo.py
```

執行完成後會產生：

- `SQL Server Express / MiniQuantDemo / dbo.prices`：範例股價資料表
- `output/equity_curve.csv`：每日淨值
- `output/trades.csv`：交易紀錄
- `output/report.html`：簡易回測報告

## 檔案對照

| 檔案 | 作用 |
|---|---|
| `run_demo.py` | 串起整套流程的入口 |
| `miniquant/config.py` | 系統參數設定 |
| `miniquant/data_loader.py` | 產生與載入範例股價資料 |
| `miniquant/indicators.py` | 技術指標計算 |
| `miniquant/factors.py` | 五因子評分與排名 |
| `miniquant/regime.py` | 市場環境判斷 |
| `miniquant/risk.py` | 停損與部位大小 |
| `miniquant/backtest.py` | 簡化回測引擎 |
| `miniquant/report.py` | CSV 與 HTML 報告輸出 |
