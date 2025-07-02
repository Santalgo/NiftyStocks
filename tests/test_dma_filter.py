import pandas as pd
from nse_fno_scanner.dma_filter import compute_dmas


def test_compute_dmas():
    data = pd.DataFrame({"Close": range(1, 301)})
    df = compute_dmas(data)
    assert not df["50DMA"].isna().all()
    assert not df["200DMA"].isna().all()
    last = df.iloc[-1]
    assert last["50DMA"] > last["200DMA"]
