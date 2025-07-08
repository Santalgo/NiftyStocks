import types
import sys

from nse_fno_scanner.strategy_loader import load_strategy


def test_load_strategy():
    mod = types.ModuleType("mymod")
    def strat(symbols):
        return [s for s in symbols if s != "B"]
    mod.my = strat
    sys.modules["mymod"] = mod
    func = load_strategy("mymod:my")
    assert func(["A", "B", "C"]) == ["A", "C"]

