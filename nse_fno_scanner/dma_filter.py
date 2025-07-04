"""Utilities for filtering stocks using daily and intraday moving averages."""

from typing import Iterable, List

import logging

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from .intraday_scanner import compute_emas, pattern_confirmed

logger = logging.getLogger(__name__)


def compute_dmas(data: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.DataFrame:
    """Compute exponential moving averages for the given periods."""

    df = data.copy()
    df[f"EMA{fast}"] = df["Close"].ewm(span=fast, adjust=False).mean()
    df[f"EMA{slow}"] = df["Close"].ewm(span=slow, adjust=False).mean()
    return df


def filter_by_dma(
    symbols: Iterable[str],
    offset: int = 1,
    *,
    fast_period: int = 20,
    slow_period: int = 50,
    higher_interval: str = "1d",
    lower_interval: str = "15m",
    higher_period: str = "100d",
    lower_period: str = "3d",
    lower_offset: int = 0,
) -> List[str]:
    """Filter symbols using daily and intraday moving averages.

    Parameters
    ----------
    symbols : Iterable[str]
        Ticker symbols to evaluate.
    offset : int, optional
        Number of latest higher timeframe candles to ignore when checking
        moving averages.
    fast_period : int, optional
        Period for the fast EMA. Defaults to ``20``.
    slow_period : int, optional
        Period for the slow EMA. Defaults to ``50``.
    higher_interval : str, optional
        Time interval for the higher timeframe download. Defaults to ``1d``.
    lower_interval : str, optional
        Time interval for the lower timeframe download. Defaults to ``15m``.
    higher_period : str, optional
        Historical period for the higher timeframe download. Defaults to ``100d``.
    lower_period : str, optional
        Historical period for the lower timeframe download. Defaults to ``3d``.
    lower_offset : int, optional
        Number of most recent lower timeframe candles to ignore when evaluating
        intraday conditions. Defaults to ``0``.

    Returns
    -------
    List[str]
        Symbols passing both daily and intraday conditions.
    """
    shortlisted = []
    for symbol in tqdm(list(symbols), desc="DMA filter"):
        try:
            logger.debug("Downloading daily data for %s", symbol)
            df = yf.download(
                f"{symbol}.NS",
                period=higher_period,
                interval=higher_interval,
                progress=False,
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
        row = df.iloc[-(offset + 1)]  # exclude recent `offset` days
        if row[f"EMA{fast_period}"] <= row[f"EMA{slow_period}"]:
            continue

        try:
            logger.debug("Downloading intraday data for %s", symbol)
            intra = yf.download(
                f"{symbol}.NS",
                period=lower_period,
                interval=lower_interval,
                progress=False,
                multi_level_index=False,
            )
            if isinstance(intra.columns, pd.MultiIndex):
                intra.columns = intra.columns.get_level_values(0)
        except Exception as exc:
            logger.debug("Failed to download intraday %s: %s", symbol, exc)
            continue
        if intra.empty or len(intra) < slow_period or len(intra) <= lower_offset + 4:
            continue
        intra = compute_emas(intra, fast=fast_period, slow=slow_period)
        subset = intra.iloc[: -(lower_offset)] if lower_offset else intra
        last_row = intra.iloc[-(lower_offset + 1)]
        if (
            last_row[f"EMA{fast_period}"] >= last_row[f"EMA{slow_period}"]
            and pattern_confirmed(subset)
        ):
            shortlisted.append(symbol)
            logger.debug("%s passed DMA filter", symbol)
    return shortlisted
