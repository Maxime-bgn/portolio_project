import sys
import os
import json
from datetime import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_fetcher import fetch_multiple_assets, get_current_prices
from portfolio_module.portfolio_core import (
    create_equal_weights, analyze_portfolio, calculate_returns
)

def generate_daily_report():
    print("Starting daily report generation at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    assets = ["AAPL", "MSFT", "GOOGL", "XLF", "GLD"]
    
    try:
        df = fetch_multiple_assets(assets, "1mo")
        
        if df.empty:
            print("ERROR: Unable to fetch data")
            return
        
        weights = create_equal_weights(assets)
        analysis = analyze_portfolio(df, weights)
        
        prices = get_current_prices(assets)
        
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "portfolio_metrics": {
                "annual_return": float(analysis["portfolio"]["annual_return"]),
                "volatility": float(analysis["portfolio"]["volatility"]),
                "sharpe_ratio": float(analysis["portfolio"]["sharpe_ratio"]),
                "max_drawdown": float(analysis["portfolio"]["max_drawdown"])
            },
            "current_prices": {
                ticker: {
                    "price": float(info["price"]),
                    "change": float(info["change"])
                }
                for ticker, info in prices.items()
            },
            "assets": {
                asset: {
                    "return": float(metrics["return"]),
                    "volatility": float(metrics["volatility"]),
                    "sharpe": float(metrics["sharpe"]),
                    "weight": float(metrics["weight"])
                }
                for asset, metrics in analysis["assets"].items()
            }
        }
        
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = os.path.join(reports_dir, "daily_report_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json")
        
        with open(filename, "w") as f:
            json.dump(report, f, indent=4)
        
        print("SUCCESS: Report generated at " + filename)
        
    except Exception as e:
        print("ERROR: " + str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_daily_report()