"""Retrieve the official NSE F&O equity symbol list."""

from typing import List

import logging

import pandas as pd

FNO_LIST_URL = "https://archives.nseindia.com/content/fo/fo_mktlots.csv"

logger = logging.getLogger(__name__)


def fetch_fno_list(url: str = FNO_LIST_URL) -> List[str]:
    """Download the NSE F&O stock list from ``url`` and return equity symbols.

    Returns
    -------
    List[str]
        List of equity ticker symbols available in F&O segment.
    """
    logger.debug("Downloading F&O list from %s", url)
    try:
        df = pd.read_csv(url)
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch F&O list: {exc}") from exc

    if "SYMBOL" in df.columns:
        col = df["SYMBOL"]
    elif len(df.columns) == 1:
        col = df.iloc[:, 0]
    else:
        raise ValueError("CSV does not contain SYMBOL column")

    symbols = col.dropna().astype(str).unique().tolist()
    return symbols
