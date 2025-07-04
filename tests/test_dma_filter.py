import os
import sys
import pandas as pd
import yfinance as yf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nse_fno_scanner.dma_filter import compute_dmas, filter_by_dma


def test_compute_dmas():
    data = pd.DataFrame({"Close": range(1, 61)})
    df = compute_dmas(data)
    assert "DMA20" in df.columns and "DMA50" in df.columns
    assert not df["DMA20"].isna().all()
    assert not df["DMA50"].isna().all()
    last = df.iloc[-1]
    assert last["DMA20"] > last["DMA50"]


def test_filter_by_dma_handles_multiindex(monkeypatch):
    dates = pd.date_range("2020-01-01", periods=60)
    close = pd.Series(range(1, 61), index=dates)
    daily = pd.DataFrame({("Close", "TEST"): close, ("Open", "TEST"): close})

    def fake_download(symbol, *args, **kwargs):
        return daily

    monkeypatch.setattr(yf, "download", fake_download)
    out = filter_by_dma(["TEST"], offset=1)
    assert out == ["TEST"]


def test_filter_by_dma_offset(monkeypatch):
    daily = pd.DataFrame({"Close": range(1, 61), "Open": range(1, 61)})

    def fake_download(symbol, *args, **kwargs):
        return daily

    monkeypatch.setattr(yf, "download", fake_download)
    out = filter_by_dma(["TEST"], offset=1)
    assert out == ["TEST"]
