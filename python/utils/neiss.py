"""Read NEISS files and apply the burn and head-injury case definitions."""

from pathlib import Path

import numpy as np
import pandas as pd

BURN_DIAG = [46, 47, 48, 49, 51]  # burns: electrical, not specified, scald, chemical, thermal
HEAD_DIAG = [52, 57, 58, 59, 62]  # concussion, fracture, hematoma, laceration, internal injury
HEAD_BDPT = [75]  # body part: head

KEEP = ["nek", "trmt_date", "age", "sex", "bdpt", "diag", "bdpt2", "diag2",
        "disp", "loc", "fmv", "prod1", "prod2", "psu", "wt"]


def read_year(path: Path, keep_narrative: bool = False) -> pd.DataFrame:
    """Read one NEISS year file into a common set of columns.

    Args:
        path: a NEISS file for one year.
        keep_narrative: also return the narrative text, joined across fields.

    Returns:
        One row per emergency department visit, lowercase column names.
    """
    if path.suffix == ".sas7bdat":
        df = pd.read_sas(path, encoding="latin1")
    else:
        df = pd.read_csv(path, parse_dates=["trmt_date"])
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(columns={"gender": "sex"})
    for col in ["bdpt2", "diag2"]:
        if col not in df.columns:
            df[col] = np.nan
    cols = [c for c in KEEP if c in df.columns]  # demo files omit record and hospital IDs
    if keep_narrative:
        narr = [c for c in ["narr1", "narr2"] if c in df.columns]
        df["narrative"] = df[narr].fillna("").astype(str).agg("".join, axis=1)
        cols.append("narrative")
    return df[cols]


def read_years(folder: Path, years: range, keep_narrative: bool = False) -> pd.DataFrame:
    """Read and stack several NEISS years from one folder."""
    frames = []
    for year in years:
        matches = sorted(folder.glob(f"neiss{year}.*"))
        if not matches:
            raise FileNotFoundError(f"No NEISS file for {year} in {folder}")
        frames.append(read_year(matches[0], keep_narrative))
    return pd.concat(frames, ignore_index=True)


def code_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Add age in years and the two case definitions (1 = case, 0 = not a case).

    Burn: a burn diagnosis in either diagnosis field; missing when both are blank.
    Head injury: a head-injury diagnosis on the head, in either diagnosis/body-part pair.
    """
    df = df.copy()
    months = df["age"].between(201, 223)  # NEISS codes ages under 2 as 200 + months
    df["age_years"] = np.where(months, (df["age"] - 200) / 12, df["age"])
    no_diag = df["diag"].isna() & df["diag2"].isna()
    burn = df["diag"].isin(BURN_DIAG) | df["diag2"].isin(BURN_DIAG)
    df["burn"] = np.where(no_diag, np.nan, burn.astype(float))
    head1 = df["diag"].isin(HEAD_DIAG) & df["bdpt"].isin(HEAD_BDPT)
    head2 = df["diag2"].isin(HEAD_DIAG) & df["bdpt2"].isin(HEAD_BDPT)
    df["head_injury"] = (head1 | head2).astype(int)
    return df


def case_counts(df: pd.DataFrame, definitions: list[str]) -> pd.DataFrame:
    """Cases, non-cases, missing and weighted national estimate per definition."""
    rows = []
    for name in definitions:
        col = df[name]
        rows.append({
            "definition": name,
            "cases": int((col == 1).sum()),
            "non_cases": int((col == 0).sum()),
            "missing": int(col.isna().sum()),
            "national_estimate": round(df.loc[col == 1, "wt"].sum()),
        })
    return pd.DataFrame(rows)
