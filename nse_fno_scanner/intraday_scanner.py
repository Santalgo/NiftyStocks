"""Intraday scan helpers based on EMA crossover confirmation patterns."""

from typing import Iterable, List

import pandas as pd
import yfinance as yf
from tqdm import tqdm


def compute_emas(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
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
            df = yf.download(
                f"{symbol}.NS",
                period="3d",
                interval="15m",
                progress=False,
            )
        except Exception:
            continue
        if df.empty or len(df) < 50:
            continue
        df = compute_emas(df)
        last_row = df.iloc[-1]
        if last_row["EMA20"] >= last_row["EMA50"] and pattern_confirmed(df):
            shortlisted.append(symbol)
    return shortlisted
