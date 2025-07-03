"""Retrieve the official NSE F&O equity symbol list."""

from typing import List
from pathlib import Path

import logging

import pandas as pd
import tempfile
import os

import gdown

FNO_LIST_URL = "https://archives.nseindia.com/content/fo/fo_mktlots.csv"
FNO_LOCAL_PATH = Path(__file__).resolve().parents[1] / "fno_list.csv"

logger = logging.getLogger(__name__)


def _maybe_download_google_drive(url: str) -> str:
    """Download Google Drive file if needed and return local path or original URL."""
    if "drive.google.com" not in url:
        return url

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    tmp.close()
    try:
        gdown.download(url, tmp.name, quiet=True, fuzzy=True)
        return tmp.name
    except Exception as exc:  # pragma: no cover - network errors
        os.unlink(tmp.name)
        raise RuntimeError(f"gdown download failed: {exc}") from exc


def fetch_fno_list(url: str = FNO_LIST_URL) -> List[str]:
    """Download the NSE F&O stock list from ``url`` and return equity symbols.

    Returns
    -------
    List[str]
        List of equity ticker symbols available in F&O segment.
    """

    if url == FNO_LIST_URL and FNO_LOCAL_PATH.exists():
        logger.debug("Loading F&O list from %s", FNO_LOCAL_PATH)
        df = pd.read_csv(FNO_LOCAL_PATH, header=None, names=["SYMBOL"])
    else:
        logger.debug("Downloading F&O list from %s", url)
        local_path = _maybe_download_google_drive(url)
        try:
            df = pd.read_csv(local_path)
            if local_path != url and os.path.exists(local_path):
                os.unlink(local_path)
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
