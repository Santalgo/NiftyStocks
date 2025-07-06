"""Download OHLC data for NSE stocks."""

from __future__ import annotations

import pandas as pd
import yfinance as yf


def fetch_ohlc(symbol: str, *, days: int = 30, interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLC data from Yahoo Finance for ``symbol``.

    Parameters
    ----------
    symbol : str
        NSE ticker without the ``.NS`` suffix.
    days : int, optional
        Number of days of history to request. Defaults to ``30``.
    interval : str, optional
        Data interval such as ``"1d"`` for daily or ``"15m"`` for intraday.

    Returns
    -------
    pandas.DataFrame
        DataFrame indexed by datetime containing the OHLC data.
    """

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


__all__ = ["fetch_ohlc"]
