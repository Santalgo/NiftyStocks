"""Example custom strategy for NiftyStocks.

The function below accepts an iterable of stock symbols and returns a
filtered list.
"""

from typing import Iterable, List


def only_n_symbols(symbols: Iterable[str]) -> List[str]:
    """Return symbols starting with 'N'.

    Parameters
    ----------
    symbols : Iterable[str]
        List of ticker symbols passed from the scanner.

    Returns
    -------
    List[str]
        Filtered symbols meeting this strategy's criteria.
    """
    return [s for s in symbols if s.startswith("N")]

