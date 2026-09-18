/* =====================================================================
   HR Analytics Project — SQL Server Setup Script
   Run this in SQL Server Management Studio (SSMS) or Azure Data Studio.
   Creates a REAL database + table that Power BI connects to via
   Get Data -> SQL Server (not a static file).

   DATA SOURCE: this project uses REAL, individual-level employee
   absence records — "Absenteeism at Work" (Martiniano, Ferreira, Sassi,
   2012), UCI Machine Learning Repository, license CC0 (Public Domain).
   740 genuine absence records for 36 real employees at a real courier
   company in Brazil, collected July 2007 - July 2010.

   NOTE ON KPIs NOT COVERED BY THIS TABLE: read README.md before you
   build the dashboard. Individual-level Attrition history and exact
   Salary are NOT included, because no legitimate open dataset publishes
   which named employees quit or what they were paid — that is
   confidential HR data everywhere, the same way patient billing is
   confidential in healthcare. This project ships ready to receive those
   two columns from your own company's HRIS/payroll export; see the
   README for exactly how to wire that in.
   ===================================================================== */

IF DB_ID('HRAnalyticsDB') IS NULL
BEGIN
    CREATE DATABASE HRAnalyticsDB;
END
GO

USE HRAnalyticsDB;
GO

IF OBJECT_ID('dbo.Employee_Absenteeism', 'U') IS NOT NULL
    DROP TABLE dbo.Employee_Absenteeism;
GO

CREATE TABLE dbo.Employee_Absenteeism (
    Record_ID               INT,
    Employee_ID              INT,
    Absence_Reason           NVARCHAR(60),
    Month                    NVARCHAR(15),
    Day_of_Week              NVARCHAR(15),
    Season                   NVARCHAR(15),
    Transportation_Expense   INT,
    Distance_From_Work_km    INT,
    Service_Time_Years       INT,
    Age                      INT,
    Workload_Avg_Per_Day     DECIMAL(10,2),
    Hit_Target_Pct           INT,          -- real performance-vs-target proxy
    Disciplinary_Failure     NVARCHAR(5),
    Education                NVARCHAR(20),
    Number_of_Children       INT,
    Social_Drinker           NVARCHAR(5),
    Social_Smoker            NVARCHAR(5),
    Number_of_Pets           INT,
    Weight_kg                INT,
    Height_cm                INT,
    BMI                      INT,
    Absenteeism_Hours        INT
);
GO

-- OPTIONAL: run this when you have your own company's HRIS export ready.
-- It's not populated here because no legitimate open dataset can contain
-- real individual attrition/salary records — see README.md.
IF OBJECT_ID('dbo.Employee_HR_Extra', 'U') IS NOT NULL
    DROP TABLE dbo.Employee_HR_Extra;
GO

CREATE TABLE dbo.Employee_HR_Extra (
    Employee_ID     INT PRIMARY KEY,
    Department      NVARCHAR(50),
    Job_Title       NVARCHAR(50),
    Hire_Date       DATE,
    Exit_Date       DATE NULL,        -- NULL = still employed; fill this to compute real attrition
    Monthly_Salary  DECIMAL(10,2) NULL,
    Performance_Rating INT NULL       -- e.g. 1-5, from your real performance review system
);
GO

/* =====================================================================
   Load the data — two options:

   OPTION A (recommended, no code):
     Right-click HRAnalyticsDB -> Tasks -> Import Flat File...
     Point it to "Employee_Absenteeism_Data.csv" and map it to
     dbo.Employee_Absenteeism.

   OPTION B (T-SQL BULK INSERT):
     1. Copy Employee_Absenteeism_Data.csv to a folder the SQL Server
        *service account* can read, e.g. C:\HRData\Employee_Absenteeism_Data.csv
     2. Update the FROM path below and run:
   ===================================================================== */

BULK INSERT dbo.Employee_Absenteeism
FROM 'C:\HRData\Employee_Absenteeism_Data.csv'   -- <-- change this path
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0a',
    CODEPAGE = '65001',
    TABLOCK
);
GO

SELECT COUNT(*) AS row_count FROM dbo.Employee_Absenteeism;
SELECT COUNT(DISTINCT Employee_ID) AS employee_count FROM dbo.Employee_Absenteeism;
SELECT TOP 20 * FROM dbo.Employee_Absenteeism;
GO

/* =====================================================================
   In Power BI Desktop:
     Get Data -> SQL Server database
     Server: localhost (or your machine name)
     Database: HRAnalyticsDB
     -> select dbo.Employee_Absenteeism -> Transform Data
     Apply the cleaning steps described in python/clean_data.py — Power
     Query and Python implement the same rules so both stacks agree.
   ===================================================================== */
