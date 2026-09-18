"""
clean_data.py
-------------
Step 2 of the pipeline: clean the raw employee absenteeism data. Same
cleaning philosophy as the Power Query steps in Power BI, so the SQL ->
Python -> Power BI stack all agree on the same definition of "clean
data" — rules chosen for this REAL dataset's actual quality issues:

  - Month/Reason codes of 0 mean "not specified" in the source system
  - a few Age/Service_Time values are clearly out-of-range data entry
    errors (this is real timesheet data, not a curated ML benchmark)
  - Employee_ID is the real join key; duplicate exact-duplicate rows
    are removed but repeat absence events per employee are expected and
    kept (each row is one absence event, not one employee)

Run from VS Code:
    python clean_data.py
(uses hr_extracted.csv produced by extract_from_sql.py; falls back to
the raw data file directly if that hasn't been run yet)
"""

import os
import numpy as np
import pandas as pd
import config


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    numeric_cols = [
        "Employee_ID", "Transportation_Expense", "Distance_From_Work_km",
        "Service_Time_Years", "Age", "Workload_Avg_Per_Day", "Hit_Target_Pct",
        "Number_of_Children", "Number_of_Pets", "Weight_kg", "Height_cm",
        "BMI", "Absenteeism_Hours",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # rule-based filters (mirrors Power Query steps)
    df = df[df["Age"].between(18, 75)]
    df = df[df["Service_Time_Years"].between(0, 50)]
    df = df[df["Hit_Target_Pct"].between(0, 100)]
    df = df[df["Absenteeism_Hours"].between(0, 120)]        # drop impossible outliers
    df = df.dropna(subset=["Employee_ID", "Age", "Absenteeism_Hours"])
    df = df.drop_duplicates()                                 # exact duplicate rows only

    # normalize "not specified" placeholders
    for col in ["Absence_Reason", "Month"]:
        if col in df.columns:
            df[col] = df[col].fillna("Not Specified")

    return df.reset_index(drop=True)


if __name__ == "__main__":
    src = "hr_extracted.csv" if os.path.exists("hr_extracted.csv") else config.FALLBACK_CSV_PATH
    print(f"[INFO] Reading raw data from {src}")
    raw = pd.read_csv(src)
    print(f"[INFO] Raw rows: {len(raw)}")

    cleaned = clean(raw)
    print(f"[OK] Clean rows: {len(cleaned)} "
          f"({len(raw) - len(cleaned)} rows removed by cleaning rules)")

    cleaned.to_csv("hr_clean.csv", index=False)
    print("[OK] Saved -> python/hr_clean.csv")
