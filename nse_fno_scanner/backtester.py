"""Simple backtesting utilities for the intraday EMA pattern."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import logging

import pandas as pd
import yfinance as yf

from .intraday_scanner import compute_emas, pattern_confirmed
from .dma_filter import compute_dmas

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    date: pd.Timestamp
    entry: float
    exit: float
    pct_return: float


def _download(symbol: str, period: str, interval: str) -> pd.DataFrame:
    logger.debug("Downloading backtest data for %s", symbol)
    df = yf.download(
        f"{symbol}.NS",
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=False,
        multi_level_index=False,
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def _backtest_intraday(
    symbol: str,
    *,
    period: str,
    interval: str,
    start_hour: int | None,
    fast: int,
    slow: int,
) -> List[Trade]:
    df = _download(symbol, period, interval)
    if df.empty:
        return []

    df.index = pd.DatetimeIndex(df.index)
    trades: List[Trade] = []

    for day, day_df in df.groupby(df.index.date):
        if start_hour is not None:
            day_df = day_df[day_df.index.hour >= start_hour]
        if len(day_df) < max(fast, slow, 5):
            continue
        day_df = compute_emas(day_df, fast=fast, slow=slow)
        if day_df.iloc[-1][f"EMA{fast}"] >= day_df.iloc[-1][f"EMA{slow}"] and pattern_confirmed(day_df):
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
    return trades


def _backtest_daily(
    symbol: str,
    *,
    period: str,
    fast: int,
    slow: int,
) -> List[Trade]:
    df = _download(symbol, period, "1d")
    if df.empty:
        return []

    df = compute_dmas(df, fast=fast, slow=slow)
    trades: List[Trade] = []
    for i in range(len(df) - 1):
        row = df.iloc[i]
        if i < slow - 1:
            continue
        if row[f"DMA{fast}"] <= row[f"DMA{slow}"]:
            continue
        entry = df.iloc[i + 1]["Open"]
        exit_price = df.iloc[i + 1]["Close"]
        ret = (exit_price - entry) / entry
        trades.append(Trade(df.index[i + 1], entry, exit_price, ret))
        logger.debug(
            "Daily trade %s: entry %.2f exit %.2f return %.2f%%",
            df.index[i + 1].date(),
            entry,
            exit_price,
            ret * 100,
        )
    return trades


def backtest_strategy(
    symbol: str,
    *,
    period: str = "30d",
    interval: str = "15m",
    mode: str = "intraday",
    start_hour: int | None = None,
    fast: int = 20,
    slow: int = 50,
    return_trades: bool = False,
) -> Tuple[int, float, float] | Tuple[int, float, float, List[Trade]]:
    """Backtest a strategy for ``symbol``.

    Parameters
    ----------
    mode : {"intraday", "daily", "both"}
        Which strategy to run.
    period : str
        Data period for Yahoo Finance downloads (e.g. "30d", "6mo").
    interval : str
        Candle interval for the intraday strategy.
    """

    trades: List[Trade] = []
    if mode in {"intraday", "both"}:
        trades.extend(
            _backtest_intraday(
                symbol,
                period=period,
                interval=interval,
                start_hour=start_hour,
                fast=fast,
                slow=slow,
            )
        )
    if mode in {"daily", "both"}:
        trades.extend(
            _backtest_daily(
                symbol,
                period=period,
                fast=fast,
                slow=slow,
            )
        )

    if not trades:
        return 0, 0.0, 0.0

    returns = [t.pct_return for t in trades]
    win_rate = sum(r > 0 for r in returns) / len(returns)
    avg_return = sum(returns) / len(returns)
    if return_trades:
        return len(trades), win_rate, avg_return, trades
    return len(trades), win_rate, avg_return
