"""Helper utilities."""

from __future__ import annotations

import pandas as pd


def printf(fmt: str, *args, flush: bool = True) -> None:
    """Print formatted message to stdout, similar to C printf."""
    print(fmt % args if args else fmt, flush=flush)


def flatten_yf(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse MultiIndex columns from ``yfinance`` downloads.

    The library returns a MultiIndex even for single tickers. This
    helper drops the ticker level so downstream code can access
    columns like ``Close`` normally.
    """
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    return df

