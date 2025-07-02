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
