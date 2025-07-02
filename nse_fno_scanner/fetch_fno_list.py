"""Retrieve the official NSE F&O equity symbol list."""

from typing import List

import pandas as pd

FNO_LIST_URL = "https://archives.nseindia.com/content/fo/fo_mktlots.csv"


def fetch_fno_list() -> List[str]:
    """Download the official NSE F&O stock list and return equity symbols.

    Returns
    -------
    List[str]
        List of equity ticker symbols available in F&O segment.
    """
    try:
        df = pd.read_csv(FNO_LIST_URL)
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch F&O list: {exc}") from exc

    if "SYMBOL" not in df.columns:
        raise ValueError("CSV does not contain SYMBOL column")

    symbols = df["SYMBOL"].dropna().astype(str).unique().tolist()
    return symbols
