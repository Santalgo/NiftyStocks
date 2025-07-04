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
    higher_int: str = "1d",
    lower_int: str = "15m",
) -> list[str]:
    """Run the scan and optionally notify/backtest.

    Parameters
    ----------
    fast : int, optional
        Fast EMA period for moving average checks.
    slow : int, optional
        Slow EMA period for moving average checks.
    higher_int : str, optional
        Interval for higher timeframe data.
    lower_int : str, optional
        Interval for lower timeframe data.

    Returns
    -------
    list[str]
        Symbols that passed the scan.
    """

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    if symbols is None:
        logging.debug("Fetching F&O list")
        if fno_url:
            symbols = fetch_fno_list(url=fno_url)
        else:
            symbols = fetch_fno_list()
    logging.debug("Filtering %d symbols by DMA", len(symbols))
    symbols = filter_by_dma(
        symbols,
        fast_period=fast,
        slow_period=slow,
        higher_interval=higher_int,
        lower_interval=lower_int,
    )
    logging.debug("Running intraday scan on %d symbols", len(symbols))
    results = intraday_scan(symbols)

    output.write_text("\n".join(results))
    print(f"Shortlisted stocks ({len(results)}):")
    for sym in results:
        print(sym)

    if backtest:
        print("\nBacktest results:")
        for sym in results:
            trades, win_rate, avg_ret = backtest_strategy(sym)
            print(
                f"{sym}: trades={trades}, win_rate={win_rate:.1f}%, avg_return={avg_ret:.2f}%"
            )

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
        "--higher-int",
        default="1d",
        help="Interval for higher timeframe (e.g. 1d)",
    )
    parser.add_argument(
        "--lower-int",
        default="15m",
        help="Interval for lower timeframe (e.g. 15m)",
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
    if args.schedule:
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
            higher_int=args.higher_int,
            lower_int=args.lower_int,
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
            higher_int=args.higher_int,
            lower_int=args.lower_int,
        )


if __name__ == "__main__":
    main()
