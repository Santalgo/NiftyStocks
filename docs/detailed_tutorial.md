# NiftyStocks Detailed Tutorial

This guide explains the main features of the NSE F&O scanner and shows real use
cases for each option.

## 1. Installation

Install Python dependencies with:

```bash
pip install -r requirements.txt
```

## 2. Running a basic scan

Execute the scanner with default settings:

```bash
python run_scan.py
```

Results are written to `scan_results.txt`. This file lists symbols that pass both
the daily moving average (DMA) filter and the intraday EMA pattern check.

Typical use cases:

* Quickly identify bullish stocks each morning before the market opens.
* Generate a short list of tickers for manual chart review.

## 3. Backtesting shortlisted stocks

Pass `--backtest` to run a moving-average backtest on all shortlisted
symbols. Use `--bt-mode` to choose `daily`, `intraday` or `both`.

```bash
python run_scan.py --symbols=RELIANCE,INFY --backtest
```

For each symbol, the script prints the number of trades, win rate and average
return. You can control the amount of historical data with `--bt-period` and the
interval with `--bt-interval`.

Use cases:

* Evaluate how the EMA crossover strategy would have performed on a specific
  stock.
* Compare the strategy's effectiveness across multiple tickers.

## 4. Scheduling scans

Two scheduling modes are available:

* `--schedule` – run the scan every 15 minutes (or the interval given by
  `--freq`).
* `--schedule-pred` – run periodically and print the market up probability based
  on the number of trending stocks.

Example running every 30 minutes with Telegram notifications:

```bash
python run_scan.py --schedule --freq 30 --notify
```

Use cases:

* Keep an updated list of strong stocks throughout the trading day.
* Obtain a running market strength prediction without manual intervention.

## 5. Telegram notifications

Set your bot token and chat ID as environment variables and pass `--notify`:

```bash
export TELEGRAM_TOKEN="<your-bot-token>"
export TELEGRAM_CHAT_ID="<target-chat-id>"
python run_scan.py --notify
```

A short summary message is sent when the scan finishes. This is handy for
receiving alerts on your phone.

## 6. Customising the symbol universe

You can scan a subset of tickers using the `--symbols` option:

```bash
python run_scan.py --symbols=RELIANCE,TCS
```

To use a custom F&O list from a file or URL, supply `--fno-url` or place a
`fno_list.csv` file in the project directory.

Use cases:

* Focus on a personal watch list rather than all F&O stocks.
* Integrate the scanner with your own data pipeline that produces a CSV.

## 7. Advanced options

* `--fast` / `--slow` – control the EMA periods used in the DMA filter and
  backtester.
* `--higher-int` / `--lower-int` – set the higher and lower timeframe intervals.
* `--offset` and `--lower-offset` – ignore a number of candles when evaluating
  the setup.
* `--debug` – print verbose logs useful for troubleshooting data downloads.

These options allow experimentation with different strategy parameters.

## 8. Example workflow

1. Run a scheduled scan with predictions and Telegram alerts:
   ```bash
   python run_scan.py --schedule-pred --freq 60 --notify
   ```
2. Review the periodic messages to gauge market sentiment.
3. When an interesting ticker appears, rerun the scan with `--backtest` to see
   historical performance:
   ```bash
   python run_scan.py --symbols=INFY --backtest
   ```

This sequence demonstrates how the tool can fit into a daily trading routine –
 continuous monitoring followed by deeper analysis on demand.

## 9. Simulating trades

For research purposes you can simulate the intraday strategy over a list of
symbols. The ``simulate_market`` function returns both the shortlisted stocks
and a DataFrame containing trade logs and cumulative PnL. ``plot_pnl`` provides
a quick visualisation.

```python
from nse_fno_scanner import simulate_market, plot_pnl

shortlist, df = simulate_market(["RELIANCE", "TCS"], days=10)
plot_pnl(df)
```
