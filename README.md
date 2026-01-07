# Quant B – Portfolio Analytics Dashboard (Streamlit)

Multi-asset portfolio analytics app with risk and advanced time-series tools.

## Overview
Quant B allows you to:
- Build and analyse portfolios  
- Compute risk/return metrics (Sharpe, VaR, drawdowns, etc.)  
- Run advanced analytics (Hurst exponent, variance ratio, regimes)  
- View everything in a clean Streamlit interface

---

## Project Structure
```
quant_b_final/
├── app.py # Main Streamlit app
├── portfolio_module/
│ ├── portfolio_core.py # Core metrics
│ ├── components.py # UI + charts
│ └── advanced_analytics.py # Hurst, VR test, regimes
└── utils/
├── data_fetcher.py # Yahoo Finance data
└── daily_report.py # Daily report (cron)
```
yaml
Copy code

---

## Installation
```bash
# Virtual env (optional)
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# Dependencies
pip install streamlit plotly pandas numpy yfinance scipy

# Run dashboard
streamlit run app.py
Default URL: http://localhost:8501
