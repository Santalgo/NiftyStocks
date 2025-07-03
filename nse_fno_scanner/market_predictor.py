import os
import math
from typing import List, Dict

import logging

import pandas as pd
import yfinance as yf
from telegram import Bot

logger = logging.getLogger(__name__)


def predict_index_movement(shortlisted_count: int, threshold: int = 10) -> float:
    """Estimate probability of index up move using logistic function."""
    return 1 / (1 + math.exp(-(shortlisted_count - threshold) / 5))


def _pct_change(symbol: str) -> float:
    logger.debug("Downloading index data for %s", symbol)
    df = yf.download(
        symbol,
        period="2d",
        interval="1d",
        progress=False,
        multi_level_index=False,
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if df.empty or len(df) < 2:
        return 0.0
    return df["Close"].iloc[-1] / df["Close"].iloc[0] - 1


def compare_with_indices(symbols: List[str]) -> Dict[str, float]:
    """Compare average stock change with NIFTY50 and BankNifty indices."""
    changes = []
    for sym in symbols:
        logger.debug("Downloading change data for %s", sym)
        df = yf.download(
            f"{sym}.NS",
            period="2d",
            interval="1d",
            progress=False,
            multi_level_index=False,
        )
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty or len(df) < 2:
            continue
        changes.append(df["Close"].iloc[-1] / df["Close"].iloc[0] - 1)
    avg_change = sum(changes) / len(changes) if changes else 0.0
    return {
        "stocks": avg_change,
        "nifty": _pct_change("^NSEI"),
        "banknifty": _pct_change("^NSEBANK"),
    }


def send_telegram_message(message: str) -> None:
    """Send a message via Telegram using token and chat id env vars."""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    bot = Bot(token=token)
    bot.send_message(chat_id=chat_id, text=message)
