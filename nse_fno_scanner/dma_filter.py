"""Utilities for filtering stocks using daily moving averages."""

from typing import Iterable, List

import logging

import pandas as pd
import yfinance as yf

from .utils import flatten_yf
from tqdm import tqdm

logger = logging.getLogger(__name__)


def compute_dmas(data: pd.DataFrame) -> pd.DataFrame:
    """Compute 50 and 200 day simple moving averages."""
    df = data.copy()
    df["50DMA"] = df["Close"].rolling(window=50).mean()
    df["200DMA"] = df["Close"].rolling(window=200).mean()
    return df


def filter_by_dma(symbols: Iterable[str], offset: int = 1) -> List[str]:
    """Filter symbols where 50DMA > 200DMA using last ``offset`` days excluded."""
    shortlisted = []
    for symbol in tqdm(list(symbols), desc="DMA filter"):
        try:
            logger.debug("Downloading daily data for %s", symbol)
            df = yf.download(
                f"{symbol}.NS", period="300d", interval="1d", progress=False
            )
            df = flatten_yf(df)
        except Exception as exc:
            logger.debug("Failed to download %s: %s", symbol, exc)
            continue
        if df.empty or len(df) < 200 + offset:
            continue
        df = compute_dmas(df)
        row = df.iloc[-(offset + 1)]  # exclude recent `offset` days
        if row["50DMA"] > row["200DMA"]:
            shortlisted.append(symbol)
            logger.debug("%s passed DMA filter", symbol)
    return shortlisted
