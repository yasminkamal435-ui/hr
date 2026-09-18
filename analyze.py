"""
analyze.py
----------
Step 3 of the pipeline: compute the same KPIs and breakdowns shown in
the Power BI dashboard, and save matplotlib charts as PNG files.

Run from VS Code:
    python analyze.py
(uses hr_clean.csv produced by clean_data.py)

About the four requested KPIs (Attrition, Absenteeism, Performance,
Salary) — read this before you're surprised by the output:

  - Absenteeism: fully real, computed directly from the real dataset.
  - Performance: real dataset has no performance-review score, but it
    does have "Hit_Target_Pct" — the real % of the daily workload target
    each employee met — which is used here as the performance KPI.
  - Attrition & Salary: NOT present in any real open HR dataset at
    individual level (same reason real hospital data never has patient
    billing — it's confidential everywhere). This script checks for an
    optional dbo.Employee_HR_Extra table / hr_extra.csv (Employee_ID,
    Exit_Date, Monthly_Salary, Performance_Rating) and, if you've loaded
    your own real company data into it, automatically computes real
    Attrition and Salary KPIs from it. If that table is empty or
    missing, those two sections are skipped with a clear note instead
    of being filled with invented numbers.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BG = "#05070c"
PANEL = "#0b0f16"
SKY = "#38bdf8"
SKY_DARK = "#0ea5e9"
TEXT = "#f1f7fb"
GRID = "#16202c"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": PANEL,
    "axes.edgecolor": GRID, "axes.labelcolor": TEXT,
    "xtick.color": TEXT, "ytick.color": TEXT,
    "text.color": TEXT, "grid.color": GRID,
    "font.size": 10,
})

OUT_DIR = "charts"
EXTRA_CSV = "hr_extra.csv"  # optional: your own real Employee_ID, Exit_Date, Monthly_Salary, Performance_Rating


def load_clean_data() -> pd.DataFrame:
    return pd.read_csv("hr_clean.csv")


def try_load_extra():
    """Loads your own real attrition/salary data if you've provided it."""
    if os.path.exists(EXTRA_CSV):
        extra = pd.read_csv(EXTRA_CSV)
        if len(extra) > 0:
            return extra
    try:
        from sqlalchemy import create_engine
        import config
        engine = create_engine(config.get_sqlalchemy_url())
        extra = pd.read_sql("SELECT * FROM dbo.Employee_HR_Extra", engine)
        if len(extra) > 0:
            return extra
    except Exception:
        pass
    return None


def print_kpis(df: pd.DataFrame):
    n_employees = df["Employee_ID"].nunique()
    n_events = len(df)
    total_hours = df["Absenteeism_Hours"].sum()
    avg_hours_per_event = df["Absenteeism_Hours"].mean()
    avg_hours_per_employee = df.groupby("Employee_ID")["Absenteeism_Hours"].sum().mean()
    avg_hit_target = df["Hit_Target_Pct"].mean()
    disciplinary_rate = (df["Disciplinary_Failure"] == "Yes").mean() * 100

    print("\n=== HR KPIs (real employee absence data) ===")
    print(f"Employees Tracked          : {n_employees}")
    print(f"Absence Events Logged      : {n_events}")
    print(f"Total Absenteeism Hours    : {total_hours:,.0f}")
    print(f"Avg. Hours / Absence Event : {avg_hours_per_event:.1f}")
    print(f"Avg. Hours / Employee      : {avg_hours_per_employee:.1f}")
    print(f"Avg. Hit-Target % (Perf.)  : {avg_hit_target:.1f}%")
    print(f"Disciplinary Failure Rate  : {disciplinary_rate:.1f}% of events")

    extra = try_load_extra()
    if extra is not None and "Exit_Date" in extra.columns:
        total_ee = extra["Employee_ID"].nunique()
        left = extra["Exit_Date"].notna().sum()
        attrition_rate = left / total_ee * 100 if total_ee else 0
        print(f"\n[Attrition — from your real dbo.Employee_HR_Extra data]")
        print(f"Attrition Rate              : {attrition_rate:.1f}% ({left}/{total_ee} employees)")
        if "Monthly_Salary" in extra.columns and extra["Monthly_Salary"].notna().any():
            print(f"Avg. Monthly Salary          : {extra['Monthly_Salary'].mean():,.0f}")
    else:
        print("\n[Attrition & Salary] Not computed — no real company data found in "
              "hr_extra.csv or dbo.Employee_HR_Extra. These KPIs need your own real "
              "HRIS/payroll export; no legitimate open dataset publishes named "
              "employees' exit dates or salaries. See README.md.")


def chart_absence_reason(df: pd.DataFrame):
    reasons = df[df["Absence_Reason"] != "Not Specified"]["Absence_Reason"].value_counts().head(8)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(reasons.index[::-1], reasons.values[::-1], color=SKY_DARK)
    ax.set_title("Absence Events by Reason (Top 8)", color=TEXT)
    ax.set_xlabel("Events")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/absence_by_reason.png", dpi=150, facecolor=BG)
    plt.close(fig)


def chart_hours_by_month(df: pd.DataFrame):
    month_order = ["January", "February", "March", "April", "May", "June", "July",
                   "August", "September", "October", "November", "December"]
    hours = df[df["Month"] != "Not Specified"].groupby("Month")["Absenteeism_Hours"].sum()
    hours = hours.reindex(month_order).fillna(0)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(hours.index, hours.values, color=SKY, linewidth=2, marker="o", markersize=4)
    ax.fill_between(hours.index, hours.values, color=SKY, alpha=0.15)
    ax.set_title("Total Absenteeism Hours by Month", color=TEXT)
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/hours_by_month.png", dpi=150, facecolor=BG)
    plt.close(fig)


def chart_hit_target_distribution(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(df["Hit_Target_Pct"], bins=15, color=SKY_DARK, edgecolor=BG)
    ax.set_title("Distribution of Hit-Target % (Performance Proxy)", color=TEXT)
    ax.set_xlabel("Hit Target %")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/hit_target_distribution.png", dpi=150, facecolor=BG)
    plt.close(fig)


def chart_disciplinary_vs_absence(df: pd.DataFrame):
    grp = df.groupby("Disciplinary_Failure")["Absenteeism_Hours"].mean()
    fig, ax = plt.subplots(figsize=(5, 4.5))
    ax.bar(grp.index, grp.values, color=[SKY_DARK, SKY])
    ax.set_title("Avg. Absenteeism Hours: Disciplinary Failure vs Not", color=TEXT)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/disciplinary_vs_absence.png", dpi=150, facecolor=BG)
    plt.close(fig)


def print_insights(df: pd.DataFrame):
    reasons = df[df["Absence_Reason"] != "Not Specified"]["Absence_Reason"].value_counts()
    top_reason = reasons.index[0]

    by_emp = df.groupby("Employee_ID")["Absenteeism_Hours"].sum().sort_values(ascending=False)
    top_employee_share = by_emp.head(5).sum() / by_emp.sum() * 100

    disc_hours = df.groupby("Disciplinary_Failure")["Absenteeism_Hours"].mean()

    print("\n=== Business Insights ===")
    print(f"- '{top_reason}' is the single most common documented reason for absence.")
    print(f"- The top 5 highest-absence employees account for {top_employee_share:.1f}% of all "
          f"logged absence hours — a small group driving a disproportionate share of lost time.")
    if "Yes" in disc_hours.index and "No" in disc_hours.index:
        diff = disc_hours["Yes"] - disc_hours["No"]
        direction = "higher" if diff > 0 else "lower"
        print(f"- Employees with a disciplinary failure on record average {abs(diff):.1f} hours "
              f"{direction} absenteeism than those without.")
    print("- Recommendation: prioritize a retention/engagement conversation with the small group "
          "of employees driving most absence hours, and monitor the Hit-Target % trend for early "
          "signs of disengagement before it shows up as absenteeism.")
    print("- To turn this into a full Attrition + Salary dashboard, load your company's real "
          "HRIS/payroll export into dbo.Employee_HR_Extra (see sql/setup_hr_database.sql) — "
          "the pipeline and Power BI report are already built to pick it up automatically.")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    df = load_clean_data()

    print_kpis(df)
    chart_absence_reason(df)
    chart_hours_by_month(df)
    chart_hit_target_distribution(df)
    chart_disciplinary_vs_absence(df)
    print_insights(df)

    print(f"\n[OK] Charts saved to python/{OUT_DIR}/")
