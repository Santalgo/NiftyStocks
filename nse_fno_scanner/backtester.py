"""Lightweight backtester for the EMA crossover strategy."""

from typing import Tuple

import logging

import yfinance as yf

from .utils import flatten_yf

logger = logging.getLogger(__name__)

from .intraday_scanner import compute_emas, pattern_confirmed


def backtest_strategy(symbol: str, period: str = "6mo") -> Tuple[int, float, float]:
    """Backtest the intraday strategy on daily data for a symbol.

    Parameters
    ----------
    symbol : str
        Equity ticker symbol without NSE suffix.
    period : str, optional
        Period to download historical data for (default "6mo").

    Returns
    -------
    Tuple[int, float, float]
        Number of trades, win rate percentage, average return percentage.
    """
    try:
        logger.debug("Downloading backtest data for %s", symbol)
        df = yf.download(
            f"{symbol}.NS", period=period, interval="1d", progress=False
        )
        df = flatten_yf(df)
    except Exception as exc:
        logger.debug("Failed to download %s: %s", symbol, exc)
        return 0, 0.0, 0.0
    if df.empty or len(df) < 50:
        return 0, 0.0, 0.0

    df = compute_emas(df)
    trades = []
    closes = df["Close"].reset_index(drop=True)
    for i in range(4, len(df) - 1):
        window = df.iloc[i - 4 : i + 1]
        if (
            window["EMA20"].iloc[-1] >= window["EMA50"].iloc[-1]
            and pattern_confirmed(window)
        ):
            entry = closes.iloc[i]
            exit_price = closes.iloc[i + 1]
            trades.append((exit_price - entry) / entry)
            logger.debug("Trade for %s: entry %.2f exit %.2f", symbol, entry, exit_price)

    if not trades:
        return 0, 0.0, 0.0

    win_rate = sum(1 for r in trades if r > 0) / len(trades) * 100
    avg_return = sum(trades) / len(trades) * 100
    return len(trades), win_rate, avg_return
