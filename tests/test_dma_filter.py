import os
import sys
import pandas as pd
import yfinance as yf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nse_fno_scanner.dma_filter import compute_dmas, filter_by_dma


def test_compute_dmas():
    data = pd.DataFrame({"Close": range(1, 301)})
    df = compute_dmas(data)
    assert not df["50DMA"].isna().all()
    assert not df["200DMA"].isna().all()
    last = df.iloc[-1]
    assert last["50DMA"] > last["200DMA"]


def test_filter_by_dma_handles_multiindex(monkeypatch):
    dates = pd.date_range("2020-01-01", periods=300)
    close = pd.Series(range(1, 301), index=dates)
    data = pd.DataFrame({("Close", "TEST"): close, ("Open", "TEST"): close})

    def fake_download(*args, **kwargs):
        return data

    monkeypatch.setattr(yf, "download", fake_download)
    out = filter_by_dma(["TEST"], offset=1)
    assert out == ["TEST"]
