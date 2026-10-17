"""Daily series and the PHI_040 / EARS C1-style detector."""

import numpy as np
import pandas as pd
import pytest
from utils import signals


def series(values, start="2020-01-01"):
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq="D"), dtype=float)


def test_flag_by_hand():
    s = series([10] * 7 + [12] * 7 + [15])
    mean, sd = 11, np.sqrt(14 / 13)
    assert signals.ears_c1(s, k=3).iloc[-1]["flag"]  # 15 > 11 + 3 * 1.038
    assert not signals.ears_c1(s, k=4).iloc[-1]["flag"]  # 15 < 11 + 4 * 1.038
    assert np.isclose(signals.ears_c1(s, k=3).iloc[-1]["threshold"], mean + 3 * sd)


def test_first_window_days_not_scored():
    assert len(signals.ears_c1(series(range(30)), k=2)) == 30 - 14


def test_zero_sd_rule_matches_phi040():
    r = signals.ears_c1(series([10] * 14 + [11, 10]), k=3)
    assert r.iloc[0]["sd_zero"] and r.iloc[0]["flag"]


def test_future_days_cannot_change_earlier_flags():
    rng = np.random.default_rng(1)
    a = series(rng.poisson(10, 400))
    b = a.copy()
    b.iloc[300:] = 1000
    ra, rb = signals.ears_c1(a, k=2.5), signals.ears_c1(b, k=2.5)
    cut = a.index[299]
    pd.testing.assert_frame_equal(ra.loc[:cut], rb.loc[:cut])


def test_calibrate_k_gives_target_rate():
    s = series(np.random.default_rng(2).poisson(50, 3000))
    k = signals.calibrate_k(s, s.index[0], s.index[-1])
    rate = signals.ears_c1(s, k)["flag"].mean()
    assert 0.008 <= rate <= 0.012


def test_daily_series_refuses_a_missing_day():
    df = pd.DataFrame({"trmt_date": pd.to_datetime(["2020-01-01", "2020-01-03"]),
                       "burn": [1.0, 0.0], "wt": [1.0, 1.0]})
    with pytest.raises(ValueError):
        signals.daily_series(df, "burn", "2020-01-01", "2020-01-03")


def test_daily_series_counts_and_ratio():
    df = pd.DataFrame({"trmt_date": pd.to_datetime(["2020-01-01"] * 4 + ["2020-01-02"]),
                       "burn": [1.0, 1.0, 0.0, np.nan, 1.0], "wt": [2.0, 3.0, 10.0, 99.0, 4.0]})
    s = signals.daily_series(df, "burn", "2020-01-01", "2020-01-02")
    assert list(s["count"]) == [2, 1]
    assert s.loc["2020-01-01", "ratio"] == 0.5  # unclassifiable weight 99 excluded
    assert np.isnan(s.loc["2020-01-02", "ratio"])  # no non-cases: undefined, not filled


def test_combined_workload_counts_days_not_flags():
    idx = pd.date_range("2020-01-01", periods=4, freq="D")
    a = pd.DataFrame({"flag": [True, False, True, False]}, index=idx)
    b = pd.DataFrame({"flag": [True, True, False, False]}, index=idx)
    out = signals.alert_summary({"a": a, "b": b}, {"all": (idx[0], idx[-1])})
    assert out.set_index("series").loc["any series (combined workload)", "flags"] == 3
