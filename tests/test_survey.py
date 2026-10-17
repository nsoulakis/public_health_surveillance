"""Design-based variance (Schroeder & Ault 2001) against hand-computed values."""

import numpy as np
import pandas as pd
from utils import survey


def records(rows):
    df = pd.DataFrame(rows, columns=["stratum", "psu", "wt", "case"])
    df["trmt_date"] = pd.Timestamp("2020-06-01")
    return df


TWO_STRATA = [("A", 1, 10, 1), ("A", 2, 20, 1), ("A", 3, 30, 1), ("B", 4, 5, 1), ("B", 5, 5, 1)]


def test_stratified_variance_by_hand():
    e = survey.estimate(records(TWO_STRATA), "case").iloc[0]
    # stratum A: totals 10, 20, 30; mean 20; squares 200; x 3/2 = 300. Stratum B: 0.
    assert e["estimate"] == 70 and np.isclose(e["se"] ** 2, 300)


def test_zero_case_hospital_is_in_the_variance():
    rows = TWO_STRATA + [("A", 6, 15, 0)]  # reports a visit, no cases
    e = survey.estimate(records(rows), "case").iloc[0]
    # stratum A: totals 10, 20, 30, 0; mean 15; squares 500; x 4/3
    assert np.isclose(e["se"] ** 2, 4 / 3 * 500)


def test_domain_keeps_hospitals_outside_the_domain():
    df = records(TWO_STRATA + [("A", 6, 15, 1)])
    inside = pd.Series([True] * 5 + [False])
    e = survey.estimate(df, "case", within=inside).iloc[0]
    assert e["estimate"] == 70 and np.isclose(e["se"] ** 2, 4 / 3 * 500)


def test_stability_rules():
    small = survey.estimate(records(TWO_STRATA), "case").iloc[0]
    assert not small["stable"]  # 5 records, estimate 70
    many = [("A", i % 4 + 1, 100.0, 1) for i in range(40)] + [("B", 5 + i % 3, 100.0, 1)
                                                               for i in range(40)]
    big = survey.estimate(records(many), "case").iloc[0]
    assert big["stable"] and big["cv"] <= survey.MAX_CV
