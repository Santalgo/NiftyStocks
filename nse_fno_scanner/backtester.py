"""Simple backtesting utilities for the intraday EMA pattern."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Iterable, List, Tuple

import logging

import pandas as pd
import yfinance as yf

from .intraday_scanner import compute_emas, pattern_confirmed

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    date: pd.Timestamp
    entry: float
    exit: float
    pct_return: float


def _download(symbol: str, days: int, interval: str) -> pd.DataFrame:
    logger.debug("Downloading backtest data for %s", symbol)
    df = yf.download(
        f"{symbol}.NS",
        period=f"{days}d",
        interval=interval,
        progress=False,
        auto_adjust=False,
        multi_level_index=False,
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def backtest_strategy(
    symbol: str,
    *,
    days: int = 5,
    interval: str = "15m",
    start_hour: int | None = None,
    fast: int = 20,
    slow: int = 50,
    return_trades: bool = False,
) -> Tuple[int, float, float] | Tuple[int, float, float, List[Trade]]:
    """Backtest the intraday EMA pattern for ``symbol``.

    Each day where the pattern occurs triggers a trade: buy on the first candle
    and exit on the last candle of the day.
    """

    df = _download(symbol, days, interval)
    if df.empty:
        return 0, 0.0, 0.0

    df.index = pd.DatetimeIndex(df.index)
    trades: List[Trade] = []

    for day, day_df in df.groupby(df.index.date):
        if start_hour is not None:
            day_df = day_df[day_df.index.hour >= start_hour]
        if len(day_df) < max(fast, slow, 5):
            continue
        day_df = compute_emas(day_df, fast=fast, slow=slow)
        if day_df.iloc[-1][f"EMA{fast}"] >= day_df.iloc[-1][
            f"EMA{slow}"
        ] and pattern_confirmed(day_df):
            entry = day_df["Open"].iloc[0]
            exit_price = day_df["Close"].iloc[-1]
            ret = (exit_price - entry) / entry
            trades.append(Trade(pd.Timestamp(day), entry, exit_price, ret))
            logger.debug(
                "Trade %s: entry %.2f exit %.2f return %.2f%%",
                day,
                entry,
                exit_price,
                ret * 100,
            )

    if not trades:
        return 0, 0.0, 0.0

    returns = [t.pct_return for t in trades]
    win_rate = sum(r > 0 for r in returns) / len(returns)
    avg_return = sum(returns) / len(returns)
    if return_trades:
        return len(trades), win_rate, avg_return, trades
    return len(trades), win_rate, avg_return
