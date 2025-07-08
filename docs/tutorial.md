# NiftyStocks Tutorial

This short guide walks you through running the F&O scanner for the first time.

## 1. Install dependencies
```bash
pip install -r requirements.txt
```

## 2. Run a basic scan
```bash
python run_scan.py
```
The results are stored in `scan_results.txt`.

## 3. Add Telegram notifications
Set your bot token and chat ID as environment variables and run with `--notify`:
```bash
export TELEGRAM_TOKEN="<your-bot-token>"
export TELEGRAM_CHAT_ID="<target-chat-id>"
python run_scan.py --notify
```

## 4. Customise the symbol universe
You can supply a comma separated list of tickers:
```bash
python run_scan.py --symbols=RELIANCE,INFY,TCS
```
Or pass a URL or local file via `--fno-url` if you maintain your own list.

For interactive exploration open `NiftyStocks_Colab.ipynb` on Google Colab and
execute the notebook cells sequentially.

### Simulating trades

Within a notebook you can run a quick simulation to see how the intraday
strategy performs:

```python
from nse_fno_scanner import simulate_market, plot_pnl

shortlist, df = simulate_market(["RELIANCE", "TCS"], days=10)
plot_pnl(df)
```

### Custom strategies

To apply your own scan logic, create a function that accepts and returns a list
of symbols and pass it to ``run_scan.py`` using ``--strategy``:

```bash
python run_scan.py --strategy=my_mod:my_strategy
```
