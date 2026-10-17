"""Daily surveillance series, moving-baseline z-scores and flags."""

import numpy as np
import pandas as pd


def daily_series(df: pd.DataFrame, case_col: str, date_col: str = "trmt_date",
                 weight_col: str | None = "wt") -> pd.DataFrame:
    """Daily counts, weighted counts and ratios for one case definition.

    Columns: total, case_sum, non_case_sum, ratio_to_other (cases / non-cases), and,
    when a weight column is given, wt_rto (weighted cases / weighted non-cases).
    """
    case = df[case_col] == 1
    non_case = df[case_col] == 0
    g = df.assign(case=case, non_case=non_case)
    agg = {"total": ("case", "size"), "case_sum": ("case", "sum"),
           "non_case_sum": ("non_case", "sum")}
    if weight_col:
        g = g.assign(case_wt=df[weight_col].where(case, 0),
                     non_case_wt=df[weight_col].where(non_case, 0))
        agg |= {"case_wt": ("case_wt", "sum"), "non_case_wt": ("non_case_wt", "sum")}
    daily = g.groupby(date_col).agg(**agg)
    daily["ratio_to_other"] = daily["case_sum"] / daily["non_case_sum"]
    if weight_col:
        daily["wt_rto"] = daily["case_wt"] / daily["non_case_wt"]
    return daily


def zscore_signals(series: pd.Series, window: int, threshold: float) -> pd.DataFrame:
    """Flag days whose residual is unusually high against the recent past.

    residual = today's value minus the mean of the previous `window` days.
    z = (residual minus the mean of the previous `window` residuals) / their SD.
    A day is flagged when z > threshold. The first 2 * window days are dropped
    because their baselines are incomplete.
    """
    moving_avg = series.shift(1).rolling(window, min_periods=1).mean()
    residual = series - moving_avg
    r_prev = residual.shift(1).rolling(window, min_periods=2)
    z = ((residual - r_prev.mean()) / r_prev.std()).replace([np.inf, -np.inf], np.nan)
    out = pd.DataFrame({"value": series, "moving_avg": moving_avg,
                        "residual": residual, "z": z})
    out["flag"] = out["z"] > threshold
    start = series.index.min() + pd.Timedelta(days=2 * window)
    return out[out.index >= start]


def flag_summary(results: dict) -> pd.DataFrame:
    """Days, flags and flags per 100 days for each series."""
    rows = []
    for (definition, measure), res in results.items():
        flags = int(res["flag"].sum())
        top = res["z"].idxmax()
        rows.append({"definition": definition, "measure": measure, "days": len(res),
                     "flags": flags, "flags_per_100_days": round(100 * flags / len(res), 2),
                     "top_flag_date": top.date(), "top_z": round(res["z"].max(), 2)})
    return pd.DataFrame(rows)
