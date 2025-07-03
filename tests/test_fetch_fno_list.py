import pandas as pd
from nse_fno_scanner.fetch_fno_list import fetch_fno_list


def test_custom_url(monkeypatch):
    data = pd.DataFrame({"SYMBOL": ["AAA", "BBB"]})

    def fake_read_csv(url):
        assert url == "http://example.com/fno.csv"
        return data

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)
    symbols = fetch_fno_list("http://example.com/fno.csv")
    assert symbols == ["AAA", "BBB"]


def test_plain_list(monkeypatch):
    data = pd.DataFrame({0: ["AAA", "BBB"]})

    def fake_read_csv(url):
        return data

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)
    assert fetch_fno_list("http://example.com/list.csv") == ["AAA", "BBB"]
