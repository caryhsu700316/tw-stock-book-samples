from dataclasses import dataclass

import pandas as pd

from .config import BUY_SCORE_MIN, INITIAL_CASH, REBALANCE_DAYS, SELL_SCORE_MIN
from .data_loader import load_prices
from .factors import score_candidates
from .indicators import add_indicators
from .regime import detect_regime
from .risk import calc_shares, hit_stop_loss


@dataclass
class BacktestResult:
    equity_curve: pd.DataFrame
    trades: pd.DataFrame
    summary: dict


def _max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = equity / peak - 1
    return float(dd.min() * 100)


def run_backtest(database_label: str) -> BacktestResult:
    prices = load_prices(database_label)
    indicators = add_indicators(prices)
    dates = sorted(indicators["trade_date"].unique())

    cash = INITIAL_CASH
    position = None
    trades = []
    equity_rows = []

    for day_index, trade_date in enumerate(dates):
        day_rows = indicators[indicators["trade_date"] == trade_date]
        regime = detect_regime(indicators, trade_date)
        scores = score_candidates(day_rows, regime)

        if position is not None:
            current = day_rows[day_rows["symbol"] == position["symbol"]]
            if not current.empty:
                price = float(current.iloc[0]["close"])
                score = float(scores[scores["symbol"] == position["symbol"]]["score"].iloc[0])
                should_sell = hit_stop_loss(price, position["avg_cost"]) or score < SELL_SCORE_MIN
                if should_sell:
                    cash += position["shares"] * price
                    trades.append([trade_date, "SELL", position["symbol"], position["name"], position["shares"], price, cash])
                    position = None

        can_rebalance = day_index > 25 and day_index % REBALANCE_DAYS == 0 and regime != "BEAR"
        if position is None and can_rebalance and not scores.empty:
            best = scores.iloc[0]
            if best["score"] >= BUY_SCORE_MIN:
                price = float(best["close"])
                shares = calc_shares(cash, price)
                if shares > 0:
                    cash -= shares * price
                    position = {
                        "symbol": best["symbol"],
                        "name": best["name"],
                        "shares": shares,
                        "avg_cost": price,
                    }
                    trades.append([trade_date, "BUY", best["symbol"], best["name"], shares, price, cash])

        market_value = 0.0
        if position is not None:
            current = day_rows[day_rows["symbol"] == position["symbol"]]
            if not current.empty:
                market_value = position["shares"] * float(current.iloc[0]["close"])
        equity_rows.append([trade_date, regime, cash, market_value, cash + market_value])

    equity_curve = pd.DataFrame(equity_rows, columns=["trade_date", "regime", "cash", "market_value", "equity"])
    trades_df = pd.DataFrame(trades, columns=["trade_date", "action", "symbol", "name", "shares", "price", "cash_after"])
    final_equity = float(equity_curve.iloc[-1]["equity"])
    summary = {
        "initial_cash": INITIAL_CASH,
        "final_equity": final_equity,
        "total_return_pct": (final_equity / INITIAL_CASH - 1) * 100,
        "max_drawdown_pct": _max_drawdown(equity_curve["equity"]),
    }
    return BacktestResult(equity_curve=equity_curve, trades=trades_df, summary=summary)
