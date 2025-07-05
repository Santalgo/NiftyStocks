import os
import sys
import pandas as pd
import yfinance as yf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nse_fno_scanner.simulator import simulate_market, plot_pnl


def test_simulate_market(monkeypatch):
    data = pd.DataFrame({"Open": range(1, 120), "Close": range(1, 120)})

    def fake_download(*args, **kwargs):
        return data

    monkeypatch.setattr(yf, "download", fake_download)
    shortlist, df = simulate_market(["AAA", "BBB"], days=2)
    assert shortlist == ["AAA", "BBB"]
    assert not df.empty
    assert "cum_pnl" in df.columns


def test_plot_pnl(monkeypatch):
    df = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=3), "cum_pnl": [0, 1, 2]})
    ax = plot_pnl(df)
    assert ax is not None
