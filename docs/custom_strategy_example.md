# Custom Strategy Example

This short guide shows how to define your own screening logic for NiftyStocks.
The scanner accepts a callable that receives and returns a list of symbols.

## 1. Create a strategy file

Create `examples/custom_strategy.py` with a function like:

```python
from typing import Iterable, List


def only_n_symbols(symbols: Iterable[str]) -> List[str]:
    """Return only tickers starting with "N"."""
    return [s for s in symbols if s.startswith("N")]
```

## 2. Run the scanner with your strategy

Execute `run_scan.py` and pass the import path using `--strategy`:

```bash
python run_scan.py --strategy=examples.custom_strategy:only_n_symbols
```

The function runs after the built-in daily and intraday scans and receives
whatever symbols remain at that point.

