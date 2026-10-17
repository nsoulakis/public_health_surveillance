"""Daily series, the EARS C1-style detector, and threshold calibration.

Detector: as in Nicholas Soulakis's PHI_040 (14-day baseline), with the EARS C1
structure (Hutwagner et al., Stat Med 2005;24:543-550; Emerg Infect Dis 2005;11:314-316):
a day is flagged when its value is above the mean plus k standard deviations of the
previous 14 days. k is chosen so that the calibration years give one flag per 100 days
(empirical alert rate: Jackson et al., BMC Med Inform Decis Mak 2007;7:6).
"""

import numpy as np
import pandas as pd

from .settings import TARGET_RATE, WINDOW


def daily_series(df: pd.DataFrame, case_col: str, start, end) -> pd.DataFrame:
    """One row per calendar day: sampled case visits and the weighted ratio.

    count: sampled visits that are cases (not an incidence).
    ratio: weighted cases / weighted non-cases, classified visits only.
    A calendar day with no visits at all raises an error rather than becoming a zero.
    """
    days = pd.date_range(start, end, freq="D")
    seen = pd.DatetimeIndex(df["trmt_date"].unique())
    missing = days.difference(seen)
    if len(missing):
        raise ValueError(f"{len(missing)} calendar days have no visits, first {missing[0].date()}")
    case = df[case_col] == 1
    non_case = df[case_col] == 0
    g = df.assign(case=case, case_wt=df["wt"].where(case, 0.0),
                  non_case_wt=df["wt"].where(non_case, 0.0)).groupby("trmt_date")
    out = pd.DataFrame({"count": g["case"].sum(), "case_wt": g["case_wt"].sum(),
                        "non_case_wt": g["non_case_wt"].sum()}).reindex(days, fill_value=0)
    out["ratio"] = out["case_wt"] / out["non_case_wt"].where(out["non_case_wt"] > 0)
    out.index.name = "date"
    return out


def baseline(series: pd.Series, window: int = WINDOW) -> pd.DataFrame:
    """Mean and sample SD of the previous `window` days (t-window ... t-1), no guardband."""
    prev = series.shift(1).rolling(window, min_periods=window)
    return pd.DataFrame({"value": series, "mean": prev.mean(), "sd": prev.std(ddof=1)})


def ears_c1(series: pd.Series, k: float, window: int = WINDOW) -> pd.DataFrame:
    """Flag days whose value is above mean + k * SD of the previous `window` days.

    Days without a full baseline are dropped. When the SD is zero the rule is
    value > mean, as in PHI_040; the column sd_zero marks those days.
    """
    b = baseline(series, window).dropna(subset=["mean", "sd"])
    b["threshold"] = b["mean"] + k * b["sd"]
    b["flag"] = b["value"] > b["threshold"]
    b["sd_zero"] = b["sd"] == 0
    return b


def standardized(series: pd.Series, window: int = WINDOW) -> pd.Series:
    """(value - mean) / SD against the previous `window` days; +inf when SD is zero and
    the value is above the mean."""
    b = baseline(series, window).dropna(subset=["mean", "sd"])
    with np.errstate(divide="ignore", invalid="ignore"):
        z = (b["value"] - b["mean"]) / b["sd"]
    return z.where(b["sd"] > 0, np.where(b["value"] > b["mean"], np.inf, -np.inf))


def calibrate_k(series: pd.Series, start, end, rate: float = TARGET_RATE,
                window: int = WINDOW) -> float:
    """k such that days from start to end are flagged at the target rate.

    A day is flagged when its standardized value exceeds k, so k is the (1 - rate)
    quantile of the standardized values over the calibration days, rounded to 0.01.
    """
    z = standardized(series, window).loc[start:end]
    z = z.replace(-np.inf, np.nan).dropna()
    return round(float(np.quantile(z[np.isfinite(z)], 1 - rate)), 2)


def alert_summary(results: dict, periods: dict) -> pd.DataFrame:
    """Days, flags and flags per 100 days for each series and period, plus the combined
    workload: days on which at least one series flags."""
    rows = []
    for name, (start, end) in periods.items():
        flags = {s: r.loc[start:end, "flag"] for s, r in results.items()}
        for s, f in flags.items():
            rows.append({"period": name, "series": s, "days": len(f), "flags": int(f.sum()),
                         "per_100_days": round(100 * f.mean(), 2)})
        any_flag = pd.concat(flags, axis=1).any(axis=1)
        rows.append({"period": name, "series": "any series (combined workload)",
                     "days": len(any_flag), "flags": int(any_flag.sum()),
                     "per_100_days": round(100 * any_flag.mean(), 2)})
    return pd.DataFrame(rows)


def top_flag(result: pd.DataFrame):
    """Date of the largest flagged value (PHI_040); None when nothing is flagged."""
    flagged = result[result["flag"]]
    return None if flagged.empty else flagged["value"].idxmax()
