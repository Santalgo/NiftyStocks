from nse_fno_scanner import (
    fetch_fno_list,
    filter_by_dma,
    intraday_scan,
    backtest_strategy,
    simulate_market,
    plot_pnl,
    schedule_scan_with_prediction,
    printf,
)


def test_root_exports_callable():
    assert callable(fetch_fno_list)
    assert callable(filter_by_dma)
    assert callable(intraday_scan)
    assert callable(backtest_strategy)
    assert callable(simulate_market)
    assert callable(plot_pnl)
    assert callable(schedule_scan_with_prediction)
    assert callable(printf)
