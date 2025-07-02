"""CLI entry point for running the F&O bullish setup scanner."""
import argparse
from pathlib import Path

from tqdm import tqdm

from nse_fno_scanner.fetch_fno_list import fetch_fno_list
from nse_fno_scanner.dma_filter import filter_by_dma
from nse_fno_scanner.intraday_scanner import intraday_scan


DEFAULT_LOG = Path("scan_results.txt")


def run(output: Path = DEFAULT_LOG) -> None:
    symbols = fetch_fno_list()
    symbols = filter_by_dma(symbols)
    results = intraday_scan(symbols)

    output.write_text("\n".join(results))
    print(f"Shortlisted stocks ({len(results)}):")
    for sym in results:
        print(sym)


def main() -> None:
    parser = argparse.ArgumentParser(description="NSE F&O bullish setup scanner")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_LOG,
        help="File to write scan results",
    )
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
