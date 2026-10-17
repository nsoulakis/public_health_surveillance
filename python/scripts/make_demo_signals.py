"""Build the demo files for the signals notebook from the full NEISS files.

Run from the repository root with the full files in data/raw/neiss/ (or NEISS_DIR set):
    python python/scripts/make_demo_signals.py

Writes, to data/demo/neiss/:
    neiss_daily_<definition>.csv   daily counts and ratios, full data (no records)
    neiss_linelist_records.csv     case records on each definition's top flag date
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.neiss import code_cases, read_records, read_years
from utils.settings import THRESHOLDS, WINDOW
from utils.signals import daily_series, zscore_signals

DEFINITIONS = ["burn", "head_injury"]
LINE_LIST_COLS = ["trmt_date", "age_years", "sex", "bdpt", "diag", "disp", "loc", "prod1",
                  "narrative", "burn", "head_injury"]


def main() -> None:
    """Write daily series and line-list records for demo mode."""
    folder = Path(os.environ.get("NEISS_DIR", "data/raw/neiss"))
    out = Path("data/demo/neiss")
    df = code_cases(read_years(folder, range(2014, 2024)))
    top_dates = []
    for d in DEFINITIONS:
        daily = daily_series(df, d)
        daily.to_csv(out / f"neiss_daily_{d}.csv")
        res = zscore_signals(daily["case_sum"], WINDOW, THRESHOLDS[(d, "case_sum")])
        top_dates.append(res["z"].idxmax())
    records = code_cases(read_records(folder, top_dates))
    keep = records[(records["burn"] == 1) | (records["head_injury"] == 1)]
    keep[LINE_LIST_COLS].to_csv(out / "neiss_linelist_records.csv", index=False)
    print(f"Top flag dates: {[str(t.date()) for t in top_dates]}; {len(keep)} records")


if __name__ == "__main__":
    main()
