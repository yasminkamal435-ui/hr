# HR Analytics — Integrated Data Project (Real Data Edition)

A complete data analytics project with **four connected pieces**, all
working on the exact same dataset:

| # | Piece | Tool | Folder |
|---|-------|------|--------|
| 1 | The data | CSV (source of truth for import) | `data/` |
| 2 | The database | SQL Server | `sql/` |
| 3 | The code | Python (open in VS Code) | `python/` |
| 4 | The dashboard | Power BI | `powerbi/` + `dashboard_preview/` |

## About the data — this is REAL, not simulated

> **"Absenteeism at Work"** (Martiniano, Ferreira & Sassi, 2012) — UCI
> Machine Learning Repository, license **CC0 (Public Domain)**. 740 real,
> individual-level absence records for **36 real employees at a real
> courier company in Brazil**, logged July 2007 – July 2010.
> Source: <https://archive.ics.uci.edu/dataset/445>

`data/Employee_Absenteeism_Data.csv` is that dataset with clearer column
names; each row is one real absence event (an employee can appear many
times), which is how HR absence logs actually work.


open dataset contains which *named* real employees quit and when, or what
they were paid. That's confidential HR data at every real company, for
the exact same reason real hospital data never contains patient billing
— it's private information about identifiable people, not something
that gets published for a course project to download. Any dataset online
that *does* claim to have realistic-looking attrition/salary/performance
numbers for named employees (the common "IBM HR Analytics Attrition"
Kaggle dataset, for example) is explicitly a **synthetic/fictional**
dataset built by IBM's data scientists for demos — not real records,
even though it's widely used and looks convincing.

**What this project does instead — and why it's actually a stronger
portfolio piece:** the SQL schema, Python pipeline, and Power BI report
are all built to *receive* your own company's real HRIS/payroll export.
`sql/setup_hr_database.sql` creates an empty `dbo.Employee_HR_Extra`
table (`Employee_ID, Department, Job_Title, Hire_Date, Exit_Date,
Monthly_Salary, Performance_Rating`) — load your own real data into it
(or a `python/hr_extra.csv` with the same columns) and:
- `python/analyze.py` **automatically detects it** and prints real
  Attrition Rate and Avg. Monthly Salary
- The Power BI guide (`powerbi/PowerBI_Setup_Guide.md`) has the DAX
  measures ready to drop in

This mirrors exactly how a real analytics team ships this kind of
project: build and validate the pipeline on real, legally-available data
first, then connect it to the company's private system when you have
access. That's a genuinely useful thing to be able to explain in an
interview — and honestly more impressive than a dashboard built on
invented numbers.

## Architecture — how they connect

```
data/Employee_Absenteeism_Data.csv
        │
        │  sql/setup_all.ps1  (ONE command, auto-detects your SQL Server
        │  instance, creates the DB + tables, imports the CSV)
        ▼
SQL Server: HRAnalyticsDB.dbo.Employee_Absenteeism   <-- single source of truth
   (+ empty dbo.Employee_HR_Extra, ready for your real attrition/salary data)
        │
        │  setup_all.ps1 also writes connection.txt
        ▼
connection.txt   <-- the ONE file that links everything together
        │
        ├─────────────────────┐
        ▼                      ▼
python/config.py         Power BI Desktop
(reads it automatically,   (paste Server/Database
 zero manual editing)       shown at the end of
        │                    setup_all.ps1 — the
        ▼                    only manual step left)
python/main.py
```

## Quick start

### 1. One-command SQL setup (Windows PowerShell)
```powershell
cd sql
powershell -ExecutionPolicy Bypass -File setup_all.ps1
```
Detects your local SQL Server instance, creates `HRAnalyticsDB` +
`dbo.Employee_Absenteeism` + empty `dbo.Employee_HR_Extra`, imports
`data/Employee_Absenteeism_Data.csv`, and writes `connection.txt`.

*(Prefer doing it by hand? `sql/setup_hr_database.sql` + SSMS's Import
Flat File wizard works too.)*

### 2. Run the Python pipeline (open `python/` in VS Code)
```bash
cd python
pip install -r requirements.txt
python main.py
```
Pulls the data from SQL Server, cleans it, prints KPIs + insights, and
saves charts to `python/charts/`.

### 3. Build the Power BI report
Open Power BI Desktop → `Get Data` → `SQL Server database` → paste the
Server/Database from `setup_all.ps1`. Follow `powerbi/PowerBI_Setup_Guide.md`.

### 4. Preview the target design
`dashboard_preview/HR_Overview_Dashboard.html` — open in any browser for
an interactive preview of what the finished Power BI report should look
like, driven by the real data.



**Data source & license:** Martiniano, A., Ferreira, R. P., & Sassi, R. J.
(2012), *"Application of a neuro fuzzy network in prediction of
absenteeism at work"*, 7th Iberian Conference on Information Systems and
Technologies (CISTI). Dataset hosted at the UCI Machine Learning
Repository, license CC0 (Public Domain).
