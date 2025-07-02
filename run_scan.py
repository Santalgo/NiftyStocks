"""CLI entry point for running the F&O bullish setup scanner."""
import argparse
from pathlib import Path


from nse_fno_scanner.fetch_fno_list import fetch_fno_list
from nse_fno_scanner.dma_filter import filter_by_dma
from nse_fno_scanner.intraday_scanner import intraday_scan
from nse_fno_scanner.backtester import backtest_strategy
from nse_fno_scanner.market_predictor import (
    predict_index_movement,
    compare_with_indices,
    send_telegram_message,
)


DEFAULT_LOG = Path("scan_results.txt")


def run(output: Path = DEFAULT_LOG, backtest: bool = False, notify: bool = False) -> None:
    symbols = fetch_fno_list()
    symbols = filter_by_dma(symbols)
    results = intraday_scan(symbols)

    output.write_text("\n".join(results))
    print(f"Shortlisted stocks ({len(results)}):")
    for sym in results:
        print(sym)

    if backtest:
        print("\nBacktest results:")
        for sym in results:
            trades, win_rate, avg_ret = backtest_strategy(sym)
            print(f"{sym}: trades={trades}, win_rate={win_rate:.1f}%, avg_return={avg_ret:.2f}%")

    if notify:
        prob = predict_index_movement(len(results))
        comp = compare_with_indices(results)
        msg = (
            f"Shortlisted {len(results)} stocks. "
            f"Market up probability: {prob:.1%}\n"
            f"Avg stock change: {comp['stocks']:.2%}\n"
            f"NIFTY50: {comp['nifty']:.2%}, BankNifty: {comp['banknifty']:.2%}"
        )
        send_telegram_message(msg)


def main() -> None:
    parser = argparse.ArgumentParser(description="NSE F&O bullish setup scanner")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_LOG,
        help="File to write scan results",
    )
    parser.add_argument(
        "--backtest",
        action="store_true",
        help="Run simple backtest for shortlisted stocks",
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="Send Telegram notifications",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run scan every 15 minutes",
    )
    args = parser.parse_args()
    if args.schedule:
        import time

        while True:
            run(args.output, args.backtest, args.notify)
            time.sleep(900)
    else:
        run(args.output, args.backtest, args.notify)


if __name__ == "__main__":
    main()
