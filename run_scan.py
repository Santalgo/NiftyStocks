"""CLI entry point for running the F&O bullish setup scanner."""

import argparse
import logging
from pathlib import Path


from nse_fno_scanner.fetch_fno_list import fetch_fno_list, FNO_LIST_URL
from nse_fno_scanner.dma_filter import filter_by_dma
from nse_fno_scanner.intraday_scanner import intraday_scan
from nse_fno_scanner.backtester import backtest_strategy
from nse_fno_scanner.market_predictor import (
    predict_index_movement,
    compare_with_indices,
    send_telegram_message,
)


DEFAULT_LOG = Path("scan_results.txt")


def _parse_symbols(text: str | None) -> list[str] | None:
    """Parse comma separated symbols string into a list."""
    if not text:
        return None
    return [s.strip().upper() for s in text.split(",") if s.strip()]


def run(
    output: Path = DEFAULT_LOG,
    backtest: bool = False,
    notify: bool = False,
    symbols: list[str] | None = None,
    fno_url: str | None = None,
    debug: bool = False,
    fast: int = 20,
    slow: int = 50,
    *,
    offset: int = 1,
    interval: str = "15m",
) -> list[str]:
    """Run the scan and optionally notify/backtest.

    Parameters
    ----------
    fast : int, optional
        Fast EMA period for moving average checks.
    slow : int, optional
        Slow EMA period for moving average checks.
    offset : int, optional
        Number of higher timeframe candles to ignore when applying moving
        average conditions.
    interval : str, optional
        Data interval for intraday scanning and backtesting.

    Returns
    -------
    list[str]
        Symbols that passed the scan.
    """

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    if symbols is None:
        logging.debug("Fetching F&O list")
        symbols = fetch_fno_list(url=fno_url) if fno_url else fetch_fno_list()

    logging.debug("Running daily DMA filter on %d symbols", len(symbols))
    symbols = filter_by_dma(symbols, offset=offset, fast_period=fast, slow_period=slow)
    logging.debug("Running intraday scan on %d symbols", len(symbols))
    results = intraday_scan(symbols, interval=interval)

    output.write_text("\n".join(results))
    print(f"Shortlisted stocks ({len(results)}):")
    for sym in results:
        print(sym)

    if backtest:
        print("\nBacktest results:")
        log_lines = []
        for sym in results:
            trades, win_rate, avg_ret = backtest_strategy(
                sym,
                days=5,
                interval=interval,
                fast=fast,
                slow=slow,
            )
            print(
                f"{sym}: trades={trades}, avg_return={avg_ret * 100:.2f}%, win_rate={win_rate * 100:.1f}%"
            )
            log_lines.append(f"{sym},{trades},{avg_ret * 100:.2f},{win_rate * 100:.1f}")
        Path("backtest_results.txt").write_text("\n".join(log_lines))

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

    return results


def schedule_scan(freq_minutes: int = 15, **kwargs) -> None:
    """Run :func:`run` periodically and print market prediction.

    Parameters
    ----------
    freq_minutes : int, optional
        Number of minutes between runs.
    """
    import time

    while True:
        results = run(**kwargs)
        prob = predict_index_movement(len(results))
        print(f"Predicted market up move probability: {prob:.1%}")
        time.sleep(freq_minutes * 60)


def schedule_scan_with_prediction(freq_minutes: int = 15, **kwargs) -> None:
    """Run :func:`run` periodically and print shortlisted stocks and prediction.

    Parameters
    ----------
    freq_minutes : int, optional
        Number of minutes between runs.
    """
    import time

    while True:
        results = run(**kwargs)
        prob = predict_index_movement(len(results))
        print(f"Stocks ({len(results)}): {', '.join(results)}")
        print(f"Predicted market up move probability: {prob:.1%}")
        time.sleep(freq_minutes * 60)


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
    parser.add_argument(
        "--schedule-pred",
        action="store_true",
        help="Run scan every N minutes and print predictions",
    )
    parser.add_argument(
        "--fast",
        type=int,
        default=20,
        help="Fast EMA period",
    )
    parser.add_argument(
        "--slow",
        type=int,
        default=50,
        help="Slow EMA period",
    )
    parser.add_argument(
        "--interval",
        default="15m",
        help="Candle interval for intraday scan and backtest",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=1,
        help="Higher timeframe offset in candles",
    )
    parser.add_argument(
        "--freq",
        type=int,
        default=15,
        help="Minutes between scheduled runs",
    )
    parser.add_argument(
        "--symbols",
        help="Comma separated list of ticker symbols to scan",
    )
    parser.add_argument(
        "--fno-url",
        help="Custom URL to download F&O stock list",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()
    if args.schedule_pred:
        schedule_scan_with_prediction(
            freq_minutes=args.freq,
            output=args.output,
            backtest=args.backtest,
            notify=args.notify,
            symbols=_parse_symbols(args.symbols),
            fno_url=args.fno_url,
            debug=args.debug,
            fast=args.fast,
            slow=args.slow,
            offset=args.offset,
            interval=args.interval,
        )
    elif args.schedule:
        schedule_scan(
            freq_minutes=args.freq,
            output=args.output,
            backtest=args.backtest,
            notify=args.notify,
            symbols=_parse_symbols(args.symbols),
            fno_url=args.fno_url,
            debug=args.debug,
            fast=args.fast,
            slow=args.slow,
            offset=args.offset,
            interval=args.interval,
        )
    else:
        run(
            args.output,
            args.backtest,
            args.notify,
            symbols=_parse_symbols(args.symbols),
            fno_url=args.fno_url,
            debug=args.debug,
            fast=args.fast,
            slow=args.slow,
            offset=args.offset,
            interval=args.interval,
        )


if __name__ == "__main__":
    main()
