"""Read the published NEISS files and apply the population and case definitions.

Rules and sources are listed in the project spec; the codes below cite them.
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data" / "neiss"
YEARS = range(2014, 2026)  # every published year from 2014 (second fields filled from 2019)
BURN_DIAG = [46, 47, 48, 49, 51]  # burn diagnoses: electrical, not specified, scald, chemical, thermal
HEAD_BDPT = [75]  # body part: head
BDPT_NOT_RECORDED = 87  # body part not stated or unknown: missing data, not a "no"
ADULT_AGE = 18  # adults are older than this, in years
DEFINITIONS = ["burn", "head_injury"]


ANALYSIS_FIELDS = ["trmt_date", "age", "sex", "diag", "diag2", "bdpt", "bdpt2", "disp",
                   "loc", "prod1", "stratum", "psu", "wt"]


def read_year(year: int, folder: Path = DATA, fields=None) -> pd.DataFrame:
    """One published NEISS year: one row per sampled emergency department visit.

    fields: the columns to read (all published fields when None). A requested field that
    CPSC did not publish that year (2014 has no second diagnosis or body part) is added
    as blank, so it is never mistaken for a coded value.
    """
    use = None if fields is None else (lambda c: c in fields)
    df = pd.read_csv(folder / f"neiss_{year}.csv.gz", parse_dates=["trmt_date"],
                     usecols=use, low_memory=False)
    for col in fields or []:
        if col not in df.columns:
            df[col] = np.nan
    return df


def read_years(years=YEARS, folder: Path = DATA, fields=ANALYSIS_FIELDS) -> pd.DataFrame:
    """Several published NEISS years, stacked (the analysis fields by default)."""
    return pd.concat([read_year(y, folder, fields) for y in years], ignore_index=True)


def read_formats(folder: Path = DATA) -> pd.DataFrame:
    """CPSC's code labels (FMTNAME, START, END, LABEL), surrounding spaces removed."""
    fmt = pd.read_csv(folder / "neiss_formats.csv", dtype=str)
    return fmt.apply(lambda col: col.str.strip())


def code_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Add age in years and the two case definitions.

    Each definition is 1 (case), 0 (non-case) or missing (unclassifiable).
    Age: under 2 is recorded in months as 200 + months (201-223); unknown age is 0
    (NEISS Coding Manual, January 2025, p. 11).
    Burn: a burn diagnosis in either diagnosis field; unclassifiable when both are blank.
    Head injury: the head as body part in either body-part field; unclassifiable when
    neither field holds a recorded body part (blank or 87, not recorded).
    """
    df = df.copy()
    age = df["age"].astype(float)
    months = age.between(201, 223)
    df["age_years"] = np.where(months, (age - 200) / 12, age)
    df.loc[age == 0, "age_years"] = np.nan
    no_diag = df["diag"].isna() & df["diag2"].isna()
    burn = df["diag"].isin(BURN_DIAG) | df["diag2"].isin(BURN_DIAG)
    df["burn"] = np.where(no_diag, np.nan, burn.astype(float))
    no_bdpt = (df["bdpt"].isna() | (df["bdpt"] == BDPT_NOT_RECORDED)) & \
        (df["bdpt2"].isna() | (df["bdpt2"] == BDPT_NOT_RECORDED))
    head = df["bdpt"].isin(HEAD_BDPT) | df["bdpt2"].isin(HEAD_BDPT)
    df["head_injury"] = np.where(no_bdpt, np.nan, head.astype(float))
    return df


def adults(df: pd.DataFrame) -> pd.DataFrame:
    """Visits by adults (age in years above ADULT_AGE). Unknown ages are excluded.

    Apply after code_cases, so that ages recorded in months are converted first.
    """
    return df[df["age_years"] > ADULT_AGE]


def case_counts(df: pd.DataFrame, definitions=DEFINITIONS) -> pd.DataFrame:
    """Sampled visits per definition: cases, non-cases and unclassifiable."""
    rows = []
    for name in definitions:
        col = df[name]
        rows.append({"definition": name, "cases": int((col == 1).sum()),
                     "non_cases": int((col == 0).sum()),
                     "unclassifiable": int(col.isna().sum())})
    return pd.DataFrame(rows)


def validity_report(df: pd.DataFrame, formats: pd.DataFrame) -> pd.DataFrame:
    """Per year: blank values in each coded field, and codes that are not in CPSC's formats."""
    fields = {"sex": "SEX", "bdpt": "BDYPT", "bdpt2": "BDYPT", "diag": "DIAG",
              "diag2": "DIAG", "disp": "DISP", "loc": "LOC", "prod1": "PROD"}
    year = df["trmt_date"].dt.year
    rows = []
    for col, fmt in fields.items():
        valid = set(pd.to_numeric(formats.loc[formats["FMTNAME"] == fmt, "START"],
                                  errors="coerce").dropna().astype(int))
        for y, values in df[col].groupby(year):
            present = values.dropna().astype(int)
            rows.append({"year": y, "field": col, "blank": int(values.isna().sum()),
                         "not_in_formats": int((~present.isin(valid)).sum())})
    return pd.DataFrame(rows)


def label(df: pd.DataFrame, formats: pd.DataFrame) -> pd.DataFrame:
    """Replace NEISS codes with CPSC's labels, for display only."""
    out = df.copy()
    pairs = {"sex": "SEX", "bdpt": "BDYPT", "diag": "DIAG", "disp": "DISP",
             "loc": "LOC", "prod1": "PROD"}
    for col, fmt in pairs.items():
        if col in out:
            f = formats[formats["FMTNAME"] == fmt]
            mapping = dict(zip(f["START"].astype(str), f["LABEL"]))
            out[col] = out[col].map(
                lambda v, m=mapping: m.get(str(int(v)), v) if pd.notna(v) else v)
    return out
