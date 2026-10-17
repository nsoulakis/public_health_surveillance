"""Build the small demo extract used when the full NEISS files are not present.

Run from the repository root with the full CPSC files in data/raw/neiss/ (or NEISS_DIR set):
    python python/scripts/make_demo_data.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.neiss import read_years

SEED = 20003
FRACTION = 0.02  # 2% random sample of every year


def main() -> None:
    """Write data/demo/neiss/neiss_demo.csv from the full files."""
    folder = Path(os.environ.get("NEISS_DIR", "data/raw/neiss"))
    df = read_years(folder, range(2014, 2024))
    demo = df.sample(frac=FRACTION, random_state=SEED).sort_values("trmt_date")
    demo["wt"] = demo["wt"] / FRACTION  # keep national estimates on the full scale
    demo = demo.drop(columns=["nek", "psu"])  # no record or hospital IDs in public files
    out = Path("data/demo/neiss/neiss_demo.csv")
    demo.to_csv(out, index=False)
    print(f"Wrote {len(demo):,} rows to {out}")


if __name__ == "__main__":
    main()
