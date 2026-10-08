from .config import OUTPUT_DIR
from .backtest import BacktestResult


def write_reports(result: BacktestResult) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    equity_path = OUTPUT_DIR / "equity_curve.csv"
    trades_path = OUTPUT_DIR / "trades.csv"
    report_path = OUTPUT_DIR / "report.html"

    result.equity_curve.to_csv(equity_path, index=False, encoding="utf-8-sig")
    result.trades.to_csv(trades_path, index=False, encoding="utf-8-sig")

    summary = result.summary
    html = f"""
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>MiniQuant 回測報告</title>
  <style>
    body {{ font-family: 'Microsoft JhengHei', sans-serif; margin: 32px; line-height: 1.6; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #bbb; padding: 8px; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
    th {{ background: #f2f4f8; }}
  </style>
</head>
<body>
  <h1>MiniQuant 回測報告</h1>
  <table>
    <tr><th>指標</th><th>數值</th></tr>
    <tr><td>初始資金</td><td>{summary['initial_cash']:,.0f}</td></tr>
    <tr><td>期末資產</td><td>{summary['final_equity']:,.0f}</td></tr>
    <tr><td>總報酬</td><td>{summary['total_return_pct']:.2f}%</td></tr>
    <tr><td>最大回撤</td><td>{summary['max_drawdown_pct']:.2f}%</td></tr>
  </table>
  <h2>最近 10 天淨值</h2>
  {result.equity_curve.tail(10).to_html(index=False)}
  <h2>交易紀錄</h2>
  {result.trades.to_html(index=False) if not result.trades.empty else '<p>本次回測沒有交易。</p>'}
</body>
</html>
"""
    report_path.write_text(html, encoding="utf-8")
    return str(report_path)
