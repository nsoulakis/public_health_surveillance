"""National estimates from the NEISS sample, with design-based uncertainty.

Method: Schroeder T, Ault K. The NEISS Sample (Design and Implementation) 1997 to
Present. U.S. Consumer Product Safety Commission, 2001 (estimate: eq. 3; variance:
p. 13 and Appendix 1). Stability criteria and confidence interval: CPSC, NEISS
web estimates (cpsc.gov/cgibin/NEISSQuery/webestimates.html).
"""

import numpy as np
import pandas as pd

MIN_RECORDS = 20
MIN_ESTIMATE = 1200
MAX_CV = 0.33


def hospital_totals(df: pd.DataFrame, cases: pd.Series) -> pd.DataFrame:
    """Weighted cases per hospital (PSU) within stratum.

    Every hospital that reported any visit in df is included, with zero when it had no
    cases; leaving zero-case hospitals out would understate the variance.
    """
    case_wt = df["wt"].where(cases, 0.0)
    return (df.assign(case_wt=case_wt)
              .groupby(["stratum", "psu"], as_index=False)["case_wt"].sum())


def stratified_variance(totals: pd.DataFrame) -> float:
    """Sum over strata of r/(r-1) * sum of squared deviations of hospital totals."""
    var = 0.0
    for _, g in totals.groupby("stratum"):
        r = len(g)
        if r > 1:
            x = g["case_wt"].to_numpy()
            var += r / (r - 1) * float(((x - x.mean()) ** 2).sum())
    return var


def estimate(df: pd.DataFrame, case_col: str, within: pd.Series | None = None,
             by: str = "year") -> pd.DataFrame:
    """Sampled cases, national estimate, SE, CV, 95% CI and CPSC stability, per period.

    df must hold every sampled visit (all ages), so that each reporting hospital is in
    the variance. `within` restricts the cases to a subpopulation, such as adults, as a
    domain estimate. Unstable estimates keep their row but are marked; the notebook
    shows no figure for them.
    """
    inside = pd.Series(True, index=df.index) if within is None else within
    period = df["trmt_date"].dt.year if by == "year" else df[by]
    rows = []
    for p, g in df.groupby(period):
        cases = (g[case_col] == 1) & inside.loc[g.index]
        est = float(g.loc[cases, "wt"].sum())
        se = float(np.sqrt(stratified_variance(hospital_totals(g, cases))))
        cv = se / est if est > 0 else np.nan
        stable = bool(cases.sum() >= MIN_RECORDS and est >= MIN_ESTIMATE and cv <= MAX_CV)
        rows.append({by: p, "sampled_cases": int(cases.sum()), "estimate": est, "se": se,
                     "cv": cv, "ci_low": est - 1.96 * est * cv, "ci_high": est + 1.96 * est * cv,
                     "stable": stable})
    return pd.DataFrame(rows)
