"""Read Chicago Reported Crimes and apply the domestic-incident case definition."""

from pathlib import Path

import pandas as pd

# Columns that may be published. Never: ID, case number, block, coordinates, beat, ward.
PUBLIC = ["date", "primary_type", "description", "location_description", "arrest",
          "domestic", "community_area"]


def read_crimes(path: Path) -> pd.DataFrame:
    """Read a City of Chicago 'Crimes - 2001 to Present' CSV export (published columns only).

    Dates become calendar days; Domestic and Arrest become True/False.
    """
    names = {"Date": "date", "Primary Type": "primary_type", "Description": "description",
             "Location Description": "location_description", "Arrest": "arrest",
             "Domestic": "domestic", "Community Area": "community_area"}
    df = pd.read_csv(path, usecols=list(names), dtype=str).rename(columns=names)
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y %I:%M:%S %p").dt.normalize()
    for col in ["arrest", "domestic"]:
        df[col] = df[col].str.lower().map({"true": True, "false": False})
    return df[PUBLIC]


def code_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Domestic incident: 1 when the report is flagged domestic, 0 otherwise."""
    df = df.copy()
    df["domestic_case"] = df["domestic"].astype("float")
    return df
