import os
import sys
import pandas as pd
import yfinance as yf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nse_fno_scanner.dma_filter import compute_dmas, filter_by_dma


def test_compute_dmas():
    data = pd.DataFrame({"Close": range(1, 61)})
    df = compute_dmas(data)
    assert "EMA20" in df.columns and "EMA50" in df.columns
    assert not df["EMA20"].isna().all()
    assert not df["EMA50"].isna().all()
    last = df.iloc[-1]
    assert last["EMA20"] > last["EMA50"]


def test_filter_by_dma_handles_multiindex(monkeypatch):
    dates = pd.date_range("2020-01-01", periods=60)
    close = pd.Series(range(1, 61), index=dates)
    daily = pd.DataFrame({("Close", "TEST"): close, ("Open", "TEST"): close})

    idates = pd.date_range("2020-03-01", periods=60, freq="15T")
    iclose = pd.Series(range(1, 61), index=idates)
    intraday = pd.DataFrame({("Close", "TEST"): iclose})

    def fake_download(symbol, *args, **kwargs):
        if kwargs.get("interval") == "1d":
            return daily
        return intraday

    monkeypatch.setattr(yf, "download", fake_download)
    out = filter_by_dma(["TEST"], offset=1)
    assert out == ["TEST"]
