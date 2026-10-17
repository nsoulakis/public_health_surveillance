"""Build the demo files for the crime notebook from the full Chicago crime export.

Run from the repository root with the export in data/raw/crime/:
    python python/scripts/make_demo_crime.py

Writes, to data/demo/crime/:
    crime_daily_domestic.csv     daily counts and ratios, full data (no records)
    crime_linelist_records.csv   domestic records on the top flag date and its 14-day baseline
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.crime import code_cases, read_crimes
from utils.settings import CRIME_THRESHOLDS, WINDOW
from utils.signals import daily_series, zscore_signals

LINE_LIST_COLS = ["date", "primary_type", "description", "location_description", "arrest"]


def main() -> None:
    """Write the daily series and the line-list records for demo mode."""
    src = sorted(Path("data/raw/crime").glob("Crimes_*.csv"))[-1]
    out = Path("data/demo/crime")
    out.mkdir(parents=True, exist_ok=True)
    df = code_cases(read_crimes(src))
    daily = daily_series(df, "domestic_case", date_col="date", weight_col=None)
    daily.to_csv(out / "crime_daily_domestic.csv")
    res = zscore_signals(daily["case_sum"], WINDOW, CRIME_THRESHOLDS[("domestic", "case_sum")])
    top = res["z"].idxmax()
    window = (df["date"] >= top - pd.Timedelta(days=WINDOW)) & (df["date"] <= top)
    keep = df[window & (df["domestic_case"] == 1)]
    keep[LINE_LIST_COLS].to_csv(out / "crime_linelist_records.csv", index=False)
    print(f"Top flag {top.date()}; {len(keep)} records")


if __name__ == "__main__":
    main()
