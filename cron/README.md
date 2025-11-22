# Cron Job Configuration

## Overview

This directory contains scripts that run automatically via cron jobs on the Linux VM.

## Daily Report (`daily_report.py`)

Generates a daily report with key metrics for configured assets:
- Open/Close prices
- Daily change (%)
- 30-day rolling volatility
- Maximum drawdown

Reports are saved to the `/reports` directory.

## Setup Instructions

### 1. Make the script executable

```bash
chmod +x /path/to/portfolio_project/cron/daily_report.py
```

### 2. Edit crontab

```bash
crontab -e
```

### 3. Add the cron job (runs at 8pm every day)

```cron
# Portfolio Daily Report - runs at 20:00 (8pm) every day
0 20 * * * cd /path/to/portfolio_project && /usr/bin/python3 cron/daily_report.py >> /var/log/portfolio_report.log 2>&1
```

### 4. Verify cron is running

```bash
crontab -l
```

## Cron Syntax Reference

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday = 0)
│ │ │ │ │
* * * * * command
```

## Example Report Output

```
============================================================
DAILY PORTFOLIO REPORT
Generated: 2025-11-22 20:00:00
============================================================

[AAPL] - 2025-11-22
----------------------------------------
  Open:                 271.00
  Close:                271.49
  High:                 273.50
  Low:                  270.00
  Volume:          45,234,567
  Daily Change:          1.97%
  Volatility(30d):      18.45%
  Max Drawdown:        -12.34%

============================================================
END OF REPORT
============================================================
```

## Customization

Edit `daily_report.py` to modify:
- `ASSETS` list: Add/remove tickers to track
- Report format: Modify `generate_full_report()` function
- Schedule: Change cron timing as needed

## Troubleshooting

**Check if cron ran:**
```bash
grep CRON /var/log/syslog
```

**Check report output:**
```bash
cat /var/log/portfolio_report.log
```

**Test script manually:**
```bash
cd /path/to/portfolio_project
python3 cron/daily_report.py
```
