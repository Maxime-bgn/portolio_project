#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Setting up cron job for daily portfolio report..."
echo "Project directory: $PROJECT_DIR"

mkdir -p "$SCRIPT_DIR/logs"

CRON_ENTRY="0 20 * * * cd $PROJECT_DIR && /usr/bin/python3 $SCRIPT_DIR/daily_report.py >> $SCRIPT_DIR/logs/cron.log 2>&1"

if crontab -l 2>/dev/null | grep -q "daily_report.py"; then
    echo "Cron job already exists. Updating..."
    (crontab -l 2>/dev/null | grep -v "daily_report.py"; echo "$CRON_ENTRY") | crontab -
else
    echo "Adding new cron job..."
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
fi

echo "Cron job installed successfully!"
echo "Report will be generated daily at 8:00 PM"
echo "Logs location: $SCRIPT_DIR/logs/cron.log"

echo ""
echo "Running test report generation..."
python3 "$SCRIPT_DIR/daily_report.py"
