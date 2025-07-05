from __future__ import annotations

"""Market simulation utilities."""

from pathlib import Path
from typing import Iterable, Tuple, List

import pandas as pd
import matplotlib.pyplot as plt

from .backtester import backtest_strategy, Trade


def simulate_market(
    symbols: Iterable[str],
    *,
    days: int = 5,
    interval: str = "15m",
    fast: int = 20,
    slow: int = 50,
    save_path: str | None = None,
) -> Tuple[List[str], pd.DataFrame]:
    """Simulate trading on ``symbols`` using the intraday strategy.

    Parameters
    ----------
    symbols : Iterable[str]
        Symbols to backtest.
    save_path : str, optional
        If given, shortlisted symbols are written to this path one per line.

    Returns
    -------
    Tuple[List[str], pd.DataFrame]
        List of shortlisted symbols and DataFrame with trade logs and PnL.
    """

    shortlisted: List[str] = []
    logs: List[dict] = []
    for sym in symbols:
        trades, win_rate, avg_ret, trade_log = backtest_strategy(
            sym,
            days=days,
            interval=interval,
            fast=fast,
            slow=slow,
            return_trades=True,
        )
        if trades > 0:
            shortlisted.append(sym)
            for t in trade_log:
                logs.append(
                    {
                        "symbol": sym,
                        "date": t.date,
                        "entry": t.entry,
                        "exit": t.exit,
                        "pct_return": t.pct_return,
                    }
                )

    if save_path is not None:
        Path(save_path).write_text("\n".join(shortlisted))

    df = pd.DataFrame(logs)
    if not df.empty:
        df["pnl"] = df["pct_return"]
        df["cum_pnl"] = df["pnl"].cumsum()
    return shortlisted, df


def plot_pnl(df: pd.DataFrame, ax=None):
    """Plot cumulative PnL from a DataFrame returned by :func:`simulate_market`."""
    if df.empty:
        return None
    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(df["date"], df["cum_pnl"], marker="o")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative PnL")
    ax.set_title("Strategy PnL")
    return ax
