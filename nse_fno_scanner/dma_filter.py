"""Utilities for filtering stocks using simple daily moving averages."""

from typing import Iterable, List

import logging

import pandas as pd
import yfinance as yf
from tqdm import tqdm


logger = logging.getLogger(__name__)


def compute_dmas(data: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.DataFrame:
    """Return ``data`` with simple moving averages added."""

    df = data.copy()
    df[f"DMA{fast}"] = df["Close"].rolling(fast).mean()
    df[f"DMA{slow}"] = df["Close"].rolling(slow).mean()
    return df


def filter_by_dma(
    symbols: Iterable[str],
    offset: int = 1,
    *,
    fast_period: int = 20,
    slow_period: int = 50,
    period_days: int = 250,
) -> List[str]:
    """Filter symbols using daily moving averages.

    Parameters
    ----------
    symbols : Iterable[str]
        Ticker symbols to evaluate.
    offset : int, optional
        Number of latest higher timeframe candles to ignore when checking
        moving averages.
    fast_period : int, optional
        Period for the fast DMA. Defaults to ``20``.
    slow_period : int, optional
        Period for the slow DMA. Defaults to ``50``.
    period_days : int, optional
        Number of days of history to download. Defaults to ``250``.

    Returns
    -------
    List[str]
        Symbols where the fast DMA is above the slow DMA.
    """
    shortlisted = []
    for symbol in tqdm(list(symbols), desc="DMA filter"):
        try:
            logger.debug("Downloading daily data for %s", symbol)
            df = yf.download(
                f"{symbol}.NS",
                period=f"{period_days}d",
                interval="1d",
                progress=False,
                auto_adjust=False,
                multi_level_index=False,
            )
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
        except Exception as exc:
            logger.debug("Failed to download %s: %s", symbol, exc)
            continue
        if df.empty or len(df) < slow_period + offset:
            continue
        df = compute_dmas(df, fast=fast_period, slow=slow_period)
        row = df.iloc[-(offset + 1)]
        if row[f"DMA{fast_period}"] > row[f"DMA{slow_period}"]:
            shortlisted.append(symbol)
            logger.debug("%s passed DMA filter", symbol)
    return shortlisted
