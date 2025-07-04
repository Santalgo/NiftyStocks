"""Backtest the EMA crossover strategy using the ``backtrader`` library."""

from typing import Tuple

import logging

import yfinance as yf
import pandas as pd
import backtrader as bt

logger = logging.getLogger(__name__)



class EMABacktestStrategy(bt.Strategy):
    """Simple strategy implementing the intraday EMA pattern.

    The strategy buys when the fast EMA is above the slow EMA and the last
    four closes form a rising pattern. The position is closed on the next bar
    so that each trade lasts exactly one day.
    """

    params = dict(fast=20, slow=50)

    def __init__(self) -> None:
        self.ema_fast = bt.indicators.EMA(self.data.close, period=self.p.fast)
        self.ema_slow = bt.indicators.EMA(self.data.close, period=self.p.slow)
        self.entry_price = None
        self.trades: list[float] = []

    def next(self) -> None:
        if self.entry_price is not None:
            exit_price = self.data.close[0]
            self.trades.append((exit_price - self.entry_price) / self.entry_price)
            self.entry_price = None
            return

        if len(self.data) < 5:
            return
        if self.ema_fast[0] >= self.ema_slow[0]:
            closes = [self.data.close[-i] for i in range(1, 5)]
            if closes[0] > closes[1] > closes[2] > closes[3]:
                self.entry_price = self.data.close[0]


def backtest_strategy(
    symbol: str, period: str = "6mo", fast: int = 20, slow: int = 50
) -> Tuple[int, float, float]:
    """Backtest the intraday strategy on daily data for a symbol.

    Parameters
    ----------
    symbol : str
        Equity ticker symbol without NSE suffix.
    period : str, optional
        Period to download historical data for (default "6mo").
    fast : int, optional
        Fast EMA period for the strategy.
    slow : int, optional
        Slow EMA period for the strategy.

    Returns
    -------
    Tuple[int, float, float]
        Number of trades, win rate percentage, average return percentage.
    """
    try:
        logger.debug("Downloading backtest data for %s", symbol)
        df = yf.download(
            f"{symbol}.NS",
            period=period,
            interval="1d",
            progress=False,
            multi_level_index=False,
        )
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.date_range("2000-01-01", periods=len(df), freq="D")
    except Exception as exc:
        logger.debug("Failed to download %s: %s", symbol, exc)
        return 0, 0.0, 0.0
    if df.empty or len(df) < 50:
        return 0, 0.0, 0.0

    cerebro = bt.Cerebro()
    datafeed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(datafeed)
    cerebro.addstrategy(EMABacktestStrategy, fast=fast, slow=slow)
    results = cerebro.run()
    strat = results[0]
    trades = strat.trades
    if not trades:
        return 0, 0.0, 0.0
    win_rate = sum(1 for r in trades if r > 0) / len(trades) * 100
    avg_return = sum(trades) / len(trades) * 100
    return len(trades), win_rate, avg_return
