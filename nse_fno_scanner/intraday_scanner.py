"""Intraday scan helpers based on EMA crossover confirmation patterns."""

from typing import Iterable, List

import logging

import pandas as pd
import yfinance as yf
from tqdm import tqdm

logger = logging.getLogger(__name__)


def compute_emas(data: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.DataFrame:
    """Return ``data`` with exponential moving averages added.

    Parameters
    ----------
    data : pd.DataFrame
        Data containing ``Close`` prices.
    fast : int, optional
        Period for the fast EMA. Defaults to ``20``.
    slow : int, optional
        Period for the slow EMA. Defaults to ``50``.
    """

    df = data.copy()
    df[f"EMA{fast}"] = df["Close"].ewm(span=fast, adjust=False).mean()
    df[f"EMA{slow}"] = df["Close"].ewm(span=slow, adjust=False).mean()
    return df


def pattern_confirmed(df: pd.DataFrame) -> bool:
    if len(df) < 5:
        return False
    c = df["Close"]
    return (
        c.iloc[-2] > c.iloc[-3]
        and c.iloc[-1] > c.iloc[-2]
        and c.iloc[-3] > c.iloc[-4]
    )


def intraday_scan(symbols: Iterable[str]) -> List[str]:
    shortlisted = []
    for symbol in tqdm(list(symbols), desc="Intraday scan"):
        try:
            logger.debug("Downloading intraday data for %s", symbol)
            df = yf.download(
                f"{symbol}.NS",
                period="3d",
                interval="15m",
                progress=False,
                multi_level_index=False,
            )
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
        except Exception as exc:
            logger.debug("Failed to download %s: %s", symbol, exc)
            continue
        if df.empty or len(df) < 50:
            continue
        df = compute_emas(df)
        last_row = df.iloc[-1]
        if last_row["EMA20"] >= last_row["EMA50"] and pattern_confirmed(df):
            shortlisted.append(symbol)
            logger.debug("%s passed intraday scan", symbol)
    return shortlisted
