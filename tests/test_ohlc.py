import os
import sys
import pandas as pd
import yfinance as yf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nse_fno_scanner.ohlc import fetch_ohlc


def test_fetch_ohlc(monkeypatch):
    data = pd.DataFrame({"Open": [1, 2], "Close": [1, 2]})

    def fake_download(ticker, *args, **kwargs):
        assert ticker == "TEST.NS"
        assert kwargs["period"] == "30d"
        assert kwargs["interval"] == "15m"
        return data

    monkeypatch.setattr(yf, "download", fake_download)
    df = fetch_ohlc("TEST", days=30, interval="15m")
    assert df.equals(data)
