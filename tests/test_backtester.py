import os
import sys
import pandas as pd
import yfinance as yf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nse_fno_scanner import backtest_strategy


def test_backtest_strategy(monkeypatch):
    data = pd.DataFrame({"Close": list(range(1, 120))})

    def fake_download(*args, **kwargs):
        return data

    monkeypatch.setattr(yf, "download", fake_download)
    trades, win_rate, avg_ret = backtest_strategy("TEST")
    assert trades >= 0
    assert 0.0 <= win_rate <= 100.0
