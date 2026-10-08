"""
實作篇範例：用一套最小量化系統跑完整流程。

執行方式：
    python run_demo.py
"""

from miniquant.backtest import run_backtest
from miniquant.data_loader import prepare_database
from miniquant.report import write_reports


def main() -> None:
    try:
        database_label = prepare_database()
    except RuntimeError as exc:
        print(f"MiniQuant 環境尚未就緒：{exc}")
        print("處理方式：啟動 SQL Server (SQLEXPRESS)，或設定 MINIQUANT_SQL_SERVER 指向可用的 SQL Server instance。")
        raise SystemExit(1) from exc

    result = run_backtest(database_label)
    report_path = write_reports(result)

    print("=== 最小量化系統執行完成 ===")
    print(f"資料庫：{database_label}")
    print(f"交易筆數：{len(result.trades)}")
    print(f"期末資產：{result.summary['final_equity']:,.0f}")
    print(f"總報酬：{result.summary['total_return_pct']:.2f}%")
    print(f"最大回撤：{result.summary['max_drawdown_pct']:.2f}%")
    print(f"報告：{report_path}")


if __name__ == "__main__":
    main()
