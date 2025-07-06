# Backtesting Examples

This page demonstrates how to download OHLC data and run quick backtests using
both [Backtrader](https://www.backtrader.com/) and the utilities bundled with
this project.

## Fetching OHLC data

Use :func:`nse_fno_scanner.fetch_ohlc` to grab data from Yahoo Finance:

```python
from nse_fno_scanner import fetch_ohlc

# Daily bars
df_daily = fetch_ohlc("RELIANCE", days=60, interval="1d")

# 15 minute bars
df_15m = fetch_ohlc("RELIANCE", days=5, interval="15m")
```

## Backtesting with Backtrader

The snippet below implements a simple moving average crossover strategy with
Backtrader.

```python
import backtrader as bt
from nse_fno_scanner import fetch_ohlc

class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1 = bt.ind.SMA(period=20)
        sma2 = bt.ind.SMA(period=50)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)

# Load daily data for six months
df = fetch_ohlc("RELIANCE", days=180, interval="1d")

data = bt.feeds.PandasData(dataname=df)
cerebro = bt.Cerebro()
cerebro.add_strategy(SmaCross)
cerebro.add_data(data)
cerebro.run()
cerebro.plot()
```

## Using the built-in backtester

For a lightweight alternative you can use :func:`nse_fno_scanner.backtest_strategy`:

```python
from nse_fno_scanner import backtest_strategy

trades, win_rate, avg_ret = backtest_strategy(
    "RELIANCE", period="30d", interval="15m", mode="intraday"
)
print(trades, win_rate, avg_ret)
```
