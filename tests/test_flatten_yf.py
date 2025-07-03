import pandas as pd
from nse_fno_scanner.utils import flatten_yf


def test_flatten_yf_multiindex():
    idx = pd.date_range("2020-01-01", periods=2)
    cols = pd.MultiIndex.from_product([
        ["Close", "Open"], ["TEST"]
    ])
    df = pd.DataFrame([[1, 1], [2, 2]], index=idx, columns=cols)
    out = flatten_yf(df)
    assert list(out.columns) == ["Close", "Open"]

