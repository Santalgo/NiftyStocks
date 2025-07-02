import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nse_fno_scanner.intraday_scanner import compute_emas, pattern_confirmed


def test_pattern_confirmed_true():
    closes = [100, 99, 100, 101, 102]
    df = pd.DataFrame({"Close": closes})
    assert pattern_confirmed(df)


def test_pattern_confirmed_false():
    closes = [100, 101, 100, 99, 98]
    df = pd.DataFrame({"Close": closes})
    assert not pattern_confirmed(df)


def test_compute_emas():
    df = pd.DataFrame({"Close": range(1, 100)})
    out = compute_emas(df)
    assert "EMA20" in out.columns and "EMA50" in out.columns
