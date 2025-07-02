from nse_fno_scanner import (
    fetch_fno_list,
    filter_by_dma,
    intraday_scan,
    backtest_strategy,
)


def test_root_exports_callable():
    assert callable(fetch_fno_list)
    assert callable(filter_by_dma)
    assert callable(intraday_scan)
    assert callable(backtest_strategy)
