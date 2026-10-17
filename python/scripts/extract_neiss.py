"""Copy CPSC's published NEISS files into the repository, unchanged.

Source: the yearly NEISS files CPSC publishes as SAS data sets (neissYYYY.sas7bdat) and
its formats file (neiss_fmt.sas7bdat), from https://www.cpsc.gov/cgibin/neissquery/
("Archived Annual NEISS Data"). Every published field and record is kept. The only
changes are: field names lowercased; the sex field, published as Sex in most years and
gender in 2023, is named sex; whole-number codes are written without a decimal point.

Usage, from the repository root:
    python python/scripts/extract_neiss.py SOURCE_FOLDER [YEAR ...]
"""

import sys
from pathlib import Path

import pandas as pd

OUT = Path("data/neiss")
YEARS = range(2014, 2026)
GZIP = {"method": "gzip", "mtime": 0}  # fixed timestamp, so the same input gives the same file


def whole_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """Store numeric codes that hold only whole numbers as integers (blanks stay blank)."""
    for col in df.columns:
        values = df[col]
        if col != "wt" and pd.api.types.is_float_dtype(values):
            present = values.dropna()
            if (present == present.round()).all():
                df[col] = values.astype("Int64")
    return df


def extract_year(source: Path, year: int) -> int:
    """Write one published year to data/neiss/neiss_YEAR.csv.gz; return its row count."""
    df = pd.read_sas(source / f"neiss{year}.sas7bdat", encoding="latin1")
    df.columns = [c.lower() for c in df.columns]
    df = whole_numbers(df.rename(columns={"gender": "sex"}))
    df.to_csv(OUT / f"neiss_{year}.csv.gz", index=False, compression=GZIP)
    return len(df)


def extract_formats(source: Path) -> int:
    """Write CPSC's code labels to data/neiss/neiss_formats.csv."""
    fmt = pd.read_sas(source / "neiss_fmt.sas7bdat", encoding="latin1")
    fmt.to_csv(OUT / "neiss_formats.csv", index=False)
    return len(fmt)


def main() -> None:
    source = Path(sys.argv[1])
    years = [int(y) for y in sys.argv[2:]] or list(YEARS)
    OUT.mkdir(parents=True, exist_ok=True)
    print("formats", extract_formats(source))
    for year in years:
        print(year, extract_year(source, year))


if __name__ == "__main__":
    main()
