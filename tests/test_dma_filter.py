import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nse_fno_scanner.dma_filter import compute_dmas


def test_compute_dmas():
    data = pd.DataFrame({"Close": range(1, 301)})
    df = compute_dmas(data)
    assert not df["50DMA"].isna().all()
    assert not df["200DMA"].isna().all()
    last = df.iloc[-1]
    assert last["50DMA"] > last["200DMA"]

from nse_fno_scanner.dma_filter import filter_by_dma
import yfinance as yf
import numpy as np


def test_filter_by_dma_flattens(monkeypatch):
    idx = pd.date_range("2020-01-01", periods=250)
    cols = pd.MultiIndex.from_product([
        ["Open", "High", "Low", "Close", "Volume"], ["TEST"]
    ])
    data = pd.DataFrame(np.arange(250 * 5).reshape(250, 5), index=idx, columns=cols)

    def fake_download(*args, **kwargs):
        return data

    monkeypatch.setattr(yf, "download", fake_download)
    out = filter_by_dma(["TEST"])
    assert out == ["TEST"]

