"""Population and case definitions, including the intentional differences from the SAS."""

import numpy as np
import pandas as pd
from utils import neiss


def visits(**cols):
    n = len(next(iter(cols.values())))
    base = {"trmt_date": pd.Timestamp("2020-01-01"), "age": 40, "diag": 57, "diag2": np.nan,
            "bdpt": 79, "bdpt2": np.nan, "wt": 1.0, "stratum": "S", "psu": 1}
    return pd.DataFrame({k: cols.get(k, [v] * n) for k, v in base.items()})


def test_age_months_unknown_and_years():
    df = neiss.code_cases(visits(age=[201, 223, 0, 45, 19, 18]))
    assert np.allclose(df["age_years"].iloc[:2], [1 / 12, 23 / 12])
    assert np.isnan(df["age_years"].iloc[2])
    assert list(df["age_years"].iloc[3:]) == [45, 19, 18]


def test_adults_exclude_infants_unknown_and_18():
    df = neiss.adults(neiss.code_cases(visits(age=[201, 223, 0, 45, 19, 18])))
    assert sorted(df["age"]) == [19, 45]


def test_sas_age_filter_order_is_corrected():
    raw = visits(age=[201, 45])
    sas_style = raw[raw["age"] > 18]  # PHI_010: filter before converting months
    assert 201 in set(sas_style["age"])  # keeps an infant
    assert 201 not in set(neiss.adults(neiss.code_cases(raw))["age"])


def test_burn_either_field_and_unclassifiable():
    df = neiss.code_cases(visits(diag=[51, 57, 57, np.nan], diag2=[np.nan, 48, np.nan, np.nan]))
    assert list(df["burn"].iloc[:3]) == [1, 1, 0]
    assert np.isnan(df["burn"].iloc[3])


def test_head_is_body_part_75_either_field_any_diagnosis():
    df = neiss.code_cases(visits(bdpt=[75, 76, 79, np.nan], bdpt2=[np.nan, 75, np.nan, np.nan],
                                 diag=[71, 57, 52, 52]))
    assert list(df["head_injury"].iloc[:3]) == [1, 1, 0]
    assert np.isnan(df["head_injury"].iloc[3])


def test_case_counts_keep_three_states_apart():
    df = neiss.code_cases(visits(diag=[51, 57, np.nan]))
    row = neiss.case_counts(df, ["burn"]).iloc[0]
    assert (row["cases"], row["non_cases"], row["unclassifiable"]) == (1, 1, 1)


def test_sas_sum_of_codes_is_not_a_count():
    mydef = pd.Series([1, 2, 2, 1])  # PHI_010 coding: 1 = case, 2 = not
    assert mydef.sum() == 6  # PHI_040 sum(mydef): cases + 2 x non-cases
    assert (mydef == 1).sum() == 2  # the release counts cases


def test_2014_missing_second_fields_are_blank():
    df = neiss.read_year(2014, fields=neiss.ANALYSIS_FIELDS)
    assert df["bdpt2"].isna().all() and df["diag2"].isna().all()


def test_published_years_load_with_one_row_per_record():
    counts = {y: len(neiss.read_year(y, fields=["trmt_date"])) for y in (2014, 2025)}
    assert counts == {2014: 367493, 2025: 410201}


def test_body_part_not_recorded_is_missing_not_a_no():
    df = neiss.code_cases(visits(bdpt=[87, 87, 87], bdpt2=[np.nan, 75, 79]))
    assert np.isnan(df["head_injury"].iloc[0])  # only "not recorded": unclassifiable
    assert df["head_injury"].iloc[1] == 1  # head in the second field
    assert df["head_injury"].iloc[2] == 0  # a recorded body part that is not the head
