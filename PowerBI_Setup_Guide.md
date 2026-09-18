# Power BI Setup Guide — HR Analytics (Real Data Edition)

This project's Power BI report connects to the **same** `HRAnalyticsDB`
database that the Python scripts (`../python/`) also read from. The data
is a real, individual-level employee absence dataset ("Absenteeism at
Work", UCI, CC0) — see `../README.md` for the full explanation, including
which KPIs are fully real and which need your own company data.

## 1. Connect to the data source

1. Open Power BI Desktop.
2. `Get Data` → `SQL Server database`.
3. Server: `localhost` (or your machine name)
4. Database: `HRAnalyticsDB`
5. Select `dbo.Employee_Absenteeism` → **Transform Data**.
6. Also select `dbo.Employee_HR_Extra` if you've loaded your own real
   attrition/salary export into it (see README.md — optional).

## 2. Clean the data in Power Query

Mirrors `../python/clean_data.py` so both stacks agree on the same numbers:

- Keep `Age` between 18–75, `Service_Time_Years` between 0–50,
  `Hit_Target_Pct` between 0–100, `Absenteeism_Hours` between 0–120
- Remove exact duplicate rows (each remaining row is one real absence event)
- Replace blank `Absence_Reason` / `Month` with `"Not Specified"`

## 3. Data model

If you've loaded `dbo.Employee_HR_Extra`, relate it to
`dbo.Employee_Absenteeism` on `Employee_ID` (one-to-many: one employee
row → many absence events). Otherwise a single flat table is enough.

## 4. DAX measures

```DAX
Employees Tracked = DISTINCTCOUNT(Employee_Absenteeism[Employee_ID])
Total Absenteeism Hours = SUM(Employee_Absenteeism[Absenteeism_Hours])
Avg Hours per Event = AVERAGE(Employee_Absenteeism[Absenteeism_Hours])
Avg Hit Target % = AVERAGE(Employee_Absenteeism[Hit_Target_Pct])
Disciplinary Failure Rate =
DIVIDE(
    CALCULATE(COUNTROWS(Employee_Absenteeism), Employee_Absenteeism[Disciplinary_Failure] = "Yes"),
    COUNTROWS(Employee_Absenteeism)
)
```

If `dbo.Employee_HR_Extra` is populated with your real data:
```DAX
Attrition Rate =
DIVIDE(
    CALCULATE(DISTINCTCOUNT(Employee_HR_Extra[Employee_ID]), NOT ISBLANK(Employee_HR_Extra[Exit_Date])),
    DISTINCTCOUNT(Employee_HR_Extra[Employee_ID])
)
Avg Monthly Salary = AVERAGE(Employee_HR_Extra[Monthly_Salary])
```

These match what `../python/analyze.py` prints, so you can cross-check
the Power BI card values against the Python console output.

## 5. Apply the theme

`View` → `Themes` → `Browse for themes...` → select
`Black_SkyBlue_PowerBI_Theme.json` in this folder.

## 6. Build the visuals

Match the layout in `../dashboard_preview/HR_Overview_Dashboard.html`:
- KPI cards: Employees Tracked, Total Absenteeism Hours, Avg. Hours/Event,
  Avg. Hit-Target % (performance proxy), Disciplinary Failure Rate
- Slicer: Season
- Bar chart: Absence Events by Reason (Top 8)
- Line chart: Absenteeism Hours by Month
- Column chart: Employees by Education Level
- Donut chart: Disciplinary Failure breakdown
- Bar chart: Events by Season
- If `Employee_HR_Extra` is populated: add Attrition Rate and Avg. Monthly
  Salary cards, plus a bar chart of exits by department/job title

## 7. Refresh

Any time new rows are added to `dbo.Employee_Absenteeism` (or you populate
`dbo.Employee_HR_Extra` with real attrition/salary data), click
**Refresh** in Power BI — no need to re-import anything manually.
