# NiftyStocks

This repository provides a simple scanner for NSE F&O stocks looking for bullish setups based on daily and intraday moving averages.

The project is helpful when you want to quickly identify stocks gaining upward
momentum on the National Stock Exchange of India. It can run from the command
line, inside a Jupyter notebook or in Google Colab.

## Use Cases

* **Daily market scan** – run the script each morning to get a list of F&O
  stocks trending above key moving averages.
* **Telegram alerts** – combine with the ``--notify`` option to receive a quick
  summary of potential opportunities directly in Telegram.
* **Custom symbol list** – supply a CSV file or a comma separated list of
  tickers when you want to focus on a subset of stocks.
* **Research and backtesting** – import the package in your own Python scripts
  to experiment with the moving‑average filters or historical data used by the
  scanner.

## Usage

Install dependencies and run the scanner:

```bash
pip install -r requirements.txt
python run_scan.py
```

Results are written to `scan_results.txt`.

### Telegram Notifications

The scanner can send a summary message via Telegram when run with the
`--notify` flag. Set the following environment variables so the script can
authenticate with the Telegram Bot API:

```bash
export TELEGRAM_TOKEN="<your-bot-token>"
export TELEGRAM_CHAT_ID="<target-chat-id>"
```

When notifications are enabled, the script also predicts the likelihood of an
index up move. The probability is calculated from the number of trending stocks
(those passing the scan) using a logistic function.

Run the scanner with notifications enabled:

```bash
python run_scan.py --notify
```

To continuously run the scan every 15 minutes and print predictions, use

```bash
python run_scan.py --schedule-pred --freq 15
```

Additional options are available:

```
--symbols  Comma separated tickers to scan instead of full F&O list
--fno-url  Custom CSV URL for the F&O stock list
--debug    Enable debug logging output
--bt-period  Period of data for the backtester (default "6mo")
--bt-interval  Data interval for the backtester
--offset       Higher timeframe offset when checking DMAs
--lower-offset Lower timeframe offset for intraday pattern
--schedule-pred  Run scan periodically and print predictions
```

If a file named `fno_list.csv` is present in the project directory it will
be used as the default F&O list, avoiding any downloads.

The ``--fno-url`` option also accepts plain text lists with one ticker per line,
such as the list shared at:

```
https://drive.google.com/file/d/1f26r2NEPmMkZTBuh1yxoRBGsOhNoxynV/view?usp=sharing
```
Links from Google Drive are downloaded automatically using the ``gdown``
library, so the shared URL can be passed directly to ``--fno-url``.

Debug messages are printed to the console. For quick printf-style messages
within your own scripts you can use `nse_fno_scanner.printf`:

```python
from nse_fno_scanner import printf

printf("Scanning %s symbols", len(symbols))
```

## Google Colab

You can try the scanner in the browser using
[Google Colab](https://colab.research.google.com/). A ready-to-run notebook is
provided in `NiftyStocks_Colab.ipynb`.
Open the notebook on Colab, execute the setup cells to install dependencies and
optionally set the Telegram environment variables, then run the final cell to
start the scan.

## Tutorial

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the scanner**
   ```bash
   python run_scan.py
   ```
   The results are saved to `scan_results.txt` in the project directory.
3. **Enable Telegram notifications** *(optional)*
   ```bash
   export TELEGRAM_TOKEN="<your-bot-token>"
   export TELEGRAM_CHAT_ID="<target-chat-id>"
   python run_scan.py --notify
   ```
   You will receive a short summary message once the scan completes.

For notebook users, open `NiftyStocks_Colab.ipynb` on Colab and execute the
cells in order. The notebook mirrors the same steps and provides a simple way to
experiment with the scanner interactively.

The same instructions are available in [docs/tutorial.md](docs/tutorial.md) if
you prefer a standalone document.
For a deeper explanation of each option, see
[docs/detailed_tutorial.md](docs/detailed_tutorial.md).
