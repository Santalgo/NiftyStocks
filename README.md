# NiftyStocks

This repository provides a simple scanner for NSE F&O stocks looking for bullish setups based on daily and intraday moving averages.

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

Additional options are available:

```
--symbols  Comma separated tickers to scan instead of full F&O list
--fno-url  Custom CSV URL for the F&O stock list
--debug    Enable debug logging output
```

The ``--fno-url`` option also accepts plain text lists with one ticker per line,
such as the list shared at:

```
https://drive.google.com/file/d/1f26r2NEPmMkZTBuh1yxoRBGsOhNoxynV/view?usp=sharing
```

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
