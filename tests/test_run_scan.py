import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import run_scan


def test_run_with_notify(monkeypatch, tmp_path):
    monkeypatch.setattr(run_scan, "fetch_fno_list", lambda: ["A"])
    monkeypatch.setattr(run_scan, "filter_by_dma", lambda syms, **kw: syms)
    monkeypatch.setattr(run_scan, "intraday_scan", lambda syms, **kw: ["A"])
    monkeypatch.setattr(run_scan, "backtest_strategy", lambda sym, **kw: (0, 0.0, 0.0))

    sent = {}

    def fake_send(msg):
        sent["msg"] = msg

    monkeypatch.setattr(run_scan, "send_telegram_message", fake_send)
    monkeypatch.setattr(run_scan, "predict_index_movement", lambda c: 0.5)
    monkeypatch.setattr(
        run_scan,
        "compare_with_indices",
        lambda syms: {"stocks": 0.01, "nifty": 0.02, "banknifty": 0.03},
    )

    out = tmp_path / "out.txt"
    run_scan.run(out, backtest=False, notify=True)
    assert "Market up" in sent["msg"]


def test_run_with_custom_strategy(monkeypatch, tmp_path):
    monkeypatch.setattr(run_scan, "fetch_fno_list", lambda: ["A", "B"])
    monkeypatch.setattr(run_scan, "filter_by_dma", lambda syms, **kw: syms)
    monkeypatch.setattr(run_scan, "intraday_scan", lambda syms, **kw: syms)

    called = {}

    def strat(symbols):
        called["syms"] = symbols
        return [s for s in symbols if s == "B"]

    out = tmp_path / "out.txt"
    res = run_scan.run(out, extra_strategies=[strat])
    assert res == ["B"]
    assert called["syms"] == ["A", "B"]
