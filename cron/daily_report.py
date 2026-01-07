
import os
import sys
from datetime import datetime

# Ensure the project root is in sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from single_asset.data_fetcher import fetch_data
from single_asset.metrics import total_return, annualized_return, volatility, sharpe_ratio, max_drawdown

# This script generates a daily performance report for a given asset (default: AAPL).
# It fetches historical data, computes key metrics, and saves the results as a text file in the reports/ folder.

ticker = "GLE.PA"  # Asset symbol to report on
period = "1y"    # Data period (e.g., 1y = 1 year)

# 1. Fetch historical data for the asset
data = fetch_data(ticker, period)
data["returns"] = data["Close"].pct_change()
data["portfolio_value"] = data["Close"]

# 2. Compute performance metrics
report = {
    "Total Return (%)": total_return(data),
    "Annualized Return (%)": annualized_return(data),
    "Volatility (%)": volatility(data),
    "Sharpe Ratio": sharpe_ratio(data),
    "Max Drawdown (%)": max_drawdown(data),
}

# 3. Write the report to a text file in the reports/ directory
now = datetime.now().strftime("%Y-%m-%d")
reports_dir = os.path.join(PROJECT_ROOT, "reports")
os.makedirs(reports_dir, exist_ok=True)
report_path = os.path.join(reports_dir, f"daily_report_{ticker}_{now}.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write(f"Daily Report for {ticker} ({now})\n\n")
    for k, v in report.items():
        f.write(f"{k}: {v:.2f}\n")

print(f"Report generated: {report_path}")
