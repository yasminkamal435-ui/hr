<#
setup_all.ps1
-------------
Run this ONCE from PowerShell (on Windows, after installing SQL Server
Express + command line tools) to auto-wire the whole project together:

  1. Auto-detects your local SQL Server instance name
  2. Creates HRAnalyticsDB + dbo.Employee_Absenteeism (+ the empty
     dbo.Employee_HR_Extra table for your own real attrition/salary data)
  3. Imports data/Employee_Absenteeism_Data.csv into it (using bcp,
     which runs as YOU, so it avoids the classic "BULK INSERT access
     denied" issue)
  4. Writes the detected server name into connection.txt — the single
     file that python/config.py reads automatically, so Python is wired
     up with zero manual editing.
  5. Prints the exact Server/Database values to paste into Power BI
     Desktop (Get Data -> SQL Server database) — that one paste is the
     only manual step left, because Power BI Desktop is a GUI app that
     can't be scripted from the command line.

Usage (from the sql/ folder):
    powershell -ExecutionPolicy Bypass -File setup_all.ps1
#>

param(
    [string]$CsvPath = "..\data\Employee_Absenteeism_Data.csv",
    [string]$Database = "HRAnalyticsDB"
)

Write-Host "== HR Analytics Project - Auto Setup ==" -ForegroundColor Cyan

# ---------------------------------------------------------------
# 1) Auto-detect a local SQL Server instance
# ---------------------------------------------------------------
$detected = $null
$instanceKey = "HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\Instance Names\SQL"

if (Test-Path $instanceKey) {
    $props = Get-ItemProperty -Path $instanceKey -ErrorAction SilentlyContinue
    if ($props) {
        $names = $props.PSObject.Properties |
                 Where-Object { $_.Name -notmatch '^PS' } |
                 Select-Object -ExpandProperty Name
        if ($names.Count -gt 0) {
            $first = $names[0]
            if ($first -eq "MSSQLSERVER") {
                $detected = $env:COMPUTERNAME
            } else {
                $detected = "$env:COMPUTERNAME\$first"
            }
        }
    }
}

if (-not $detected) {
    Write-Host "Could not auto-detect a local SQL Server instance." -ForegroundColor Yellow
    $detected = Read-Host "Enter your server name manually (e.g. localhost\SQLEXPRESS)"
}

Write-Host "Using SQL Server instance: $detected" -ForegroundColor Green

# ---------------------------------------------------------------
# 2) Create database + tables
# ---------------------------------------------------------------
Write-Host "`nCreating database and tables..." -ForegroundColor Cyan

sqlcmd -S $detected -Q "IF DB_ID('$Database') IS NULL CREATE DATABASE $Database;"

$createTableSql = @"
IF OBJECT_ID('dbo.Employee_Absenteeism','U') IS NOT NULL DROP TABLE dbo.Employee_Absenteeism;
CREATE TABLE dbo.Employee_Absenteeism (
    Record_ID INT, Employee_ID INT, Absence_Reason NVARCHAR(60), Month NVARCHAR(15),
    Day_of_Week NVARCHAR(15), Season NVARCHAR(15), Transportation_Expense INT,
    Distance_From_Work_km INT, Service_Time_Years INT, Age INT,
    Workload_Avg_Per_Day DECIMAL(10,2), Hit_Target_Pct INT, Disciplinary_Failure NVARCHAR(5),
    Education NVARCHAR(20), Number_of_Children INT, Social_Drinker NVARCHAR(5),
    Social_Smoker NVARCHAR(5), Number_of_Pets INT, Weight_kg INT, Height_cm INT,
    BMI INT, Absenteeism_Hours INT
);
IF OBJECT_ID('dbo.Employee_HR_Extra','U') IS NOT NULL DROP TABLE dbo.Employee_HR_Extra;
CREATE TABLE dbo.Employee_HR_Extra (
    Employee_ID INT PRIMARY KEY, Department NVARCHAR(50), Job_Title NVARCHAR(50),
    Hire_Date DATE, Exit_Date DATE NULL, Monthly_Salary DECIMAL(10,2) NULL,
    Performance_Rating INT NULL
);
"@
sqlcmd -S $detected -d $Database -Q $createTableSql

# ---------------------------------------------------------------
# 3) Import the CSV using bcp (runs as the current user -> no
#    service-account file permission headaches like BULK INSERT)
# ---------------------------------------------------------------
Write-Host "`nImporting $CsvPath ..." -ForegroundColor Cyan
bcp dbo.Employee_Absenteeism in $CsvPath -S $detected -d $Database -c -t"," -r"\n" -F 2 -C 65001 -T

# ---------------------------------------------------------------
# 4) Write connection.txt — the single file that links SQL Server
#    to the Python side automatically (config.py reads this)
# ---------------------------------------------------------------
$connFile = "..\connection.txt"
"$detected`n$Database" | Out-File -Encoding utf8 $connFile
Write-Host "`nSaved connection info to $connFile" -ForegroundColor Green

# ---------------------------------------------------------------
# 5) Summary
# ---------------------------------------------------------------
Write-Host "`n== Setup complete ==" -ForegroundColor Cyan
Write-Host "Server:   $detected"
Write-Host "Database: $Database"
Write-Host ""
Write-Host "Python side: already wired up automatically via connection.txt." -ForegroundColor Green
Write-Host "Just run:  cd ..\python  &&  pip install -r requirements.txt  &&  python main.py"
Write-Host ""
Write-Host "Have real attrition/salary data from your own company? Load it into" -ForegroundColor Yellow
Write-Host "dbo.Employee_HR_Extra (created above) and re-run python/analyze.py —" -ForegroundColor Yellow
Write-Host "it auto-detects that table and adds the Attrition + Salary KPIs." -ForegroundColor Yellow
Write-Host ""
Write-Host "Power BI side: paste these two values into Get Data -> SQL Server database:" -ForegroundColor Yellow
Write-Host "  Server:   $detected"
Write-Host "  Database: $Database"
