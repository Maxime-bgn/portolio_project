# Daily Portfolio Report - Cron Job

Automated daily report generation for portfolio analytics.

## What it does

Generates a JSON report every day at 8:00 PM containing:
- Portfolio metrics (return, volatility, Sharpe ratio, max drawdown)
- Current asset prices
- Individual asset performance

## Files

- `daily_report.py` - Script that generates the report
- `setup_cron.sh` - Installation script
- `crontab_config.txt` - Cron configuration example
- `logs/` - Execution logs

## Installation
```bash
chmod +x cron/setup_cron.sh
./cron/setup_cron.sh
```

## Manual Test
```bash
python3 cron/daily_report.py
```

## Check Status
```bash
crontab -l
```

## View Logs
```bash
tail -f cron/logs/cron.log
```

## Reports Location

Reports are saved in `reports/` folder with format:
`daily_report_YYYYMMDD_HHMMSS.json`

## Schedule

Default: Every day at 8:00 PM (20:00)

To modify, edit crontab:
```bash
crontab -e
```
