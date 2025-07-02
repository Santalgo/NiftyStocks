import os
import sys
import pandas as pd
import yfinance as yf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nse_fno_scanner.market_predictor import (
    predict_index_movement,
    compare_with_indices,
    send_telegram_message,
)


def test_predict_index_movement_range():
    assert 0.0 < predict_index_movement(0) < 1.0
    high = predict_index_movement(20)
    low = predict_index_movement(0)
    assert high > low


def test_compare_with_indices(monkeypatch):
    data_map = {
        "^NSEI": pd.DataFrame({"Close": [100, 110]}),
        "^NSEBANK": pd.DataFrame({"Close": [200, 220]}),
        "TEST.NS": pd.DataFrame({"Close": [50, 55]}),
    }

    def fake_download(symbol, *args, **kwargs):
        return data_map.get(symbol, data_map["TEST.NS"])

    monkeypatch.setattr(yf, "download", fake_download)
    res = compare_with_indices(["TEST"])
    assert res["nifty"] > 0
    assert res["banknifty"] > 0
    assert res["stocks"] > 0


def test_send_telegram_message(monkeypatch):
    sent = {}

    class FakeBot:
        def __init__(self, token):
            sent["token"] = token

        def send_message(self, chat_id, text):
            sent["chat_id"] = chat_id
            sent["text"] = text

    monkeypatch.setattr("nse_fno_scanner.market_predictor.Bot", FakeBot)
    monkeypatch.setenv("TELEGRAM_TOKEN", "tkn")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "cid")
    send_telegram_message("hello")
    assert sent["token"] == "tkn"
    assert sent["chat_id"] == "cid"
    assert sent["text"] == "hello"
