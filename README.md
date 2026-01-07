# portolio_project
# Single Asset Strategy Dashboard (Streamlit)

Interactive dashboard to test and compare systematic trading strategies on a single asset.

## Overview
This app allows you to:
- Fetch and visualise price data for one ticker
- Backtest trading strategies
- Inspect cumulative performance and drawdowns
- Compare results against Buy & Hold

---

## Structure
single_asset/
├── data_fetcher.py # Retrieve historical prices
├── strategies.py # Trading strategy implementations
├── charts.py # Plotting functions
├── metrics.py # Performance metrics (Sharpe, DD, etc.)
└── app.py # Streamlit frontend

yaml
Copy code

---

## Installation
```bash
pip install streamlit pandas numpy yfinance plotly
streamlit run single_asset/app.py
Default URL:
http://localhost:8501

Included Strategies
Buy and Hold

End-of-Month

Volatility Breakout

Trend Following

Golden Cross

RSI Oversold

MACD Crossover

Metrics
Total and annualised return

Volatility

Sharpe ratio

Max drawdown

Recovery time

Notes
Designed for educational and testing purposes.
Perfect for analysing behaviour of a single ticker through a variety of rule-based signals.

yaml
Copy code

---

#  README – **Multi-Asset Portfolio Dashboard** (`FinalApp.py` / `portfolio_module`)

```markdown
# Quant B – Portfolio Analytics Dashboard (Streamlit)

Multi-asset portfolio analytics platform with performance, risk, allocation, and advanced statistical tools.

## Overview
This dashboard allows you to:
- Build multi-ticker portfolios
- Compute performance and risk metrics
- Analyse drawdowns, correlations, and asset contribution
- Run advanced regime and volatility diagnostics

---

## Structure
FinalApp.py # Main Streamlit interface
portfolio_module/
portfolio_core.py # Core calculations
advanced_analytics.py # Hurst, variance ratio, regimes
components.py # UI + charts
utils/
data_fetcher.py # Yahoo Finance data
reports/ # Report outputs (optional)

yaml
Copy code

---

## Installation
```bash
pip install streamlit pandas numpy yfinance plotly scipy
streamlit run FinalApp.py
Access via:
http://localhost:8501
