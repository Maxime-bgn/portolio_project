# Quant B – Portfolio Analytics Dashboard (Streamlit)

Multi-asset portfolio analytics app with risk and advanced time-series tools.

## Overview

Quant B allows you to:

- Build and analyze portfolios
- Compute risk/return metrics (Sharpe, VaR, drawdowns, etc.)
- Run advanced analytics (Hurst exponent, variance ratio, regimes)
- Use a clean Streamlit interface

## Project Structure

```
quant_b_final/
├── app.py                          # Main Streamlit app
├── portfolio_module/
│   ├── portfolio_core.py           # Core metrics
│   ├── components.py               # UI + charts
│   └── advanced_analytics.py       # Hurst, VR test, regimes
└── utils/
    ├── data_fetcher.py             # Price data (Yahoo Finance)
    └── daily_report.py             # Daily report script (cron)
Installation
bash
Copy code
# Optional: virtual env
python3 -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

# Dependencies
pip install streamlit plotly pandas numpy yfinance scipy

# Run app
streamlit run app.py
Default URL: http://localhost:8501

Main Pages
1. Portfolio
Price and performance (base 100)

Allocation pie chart

Drawdown curve and stats

Correlation matrix

Portfolio metrics:

Return, volatility (annualized)

Sharpe, Sortino, Calmar

Max drawdown

VaR and CVaR

Beta / Alpha vs benchmark

Asset-level table

2. Advanced Analytics
Hurst exponent by asset

Multi-scale variance

Variance Ratio (Lo–MacKinlay)

Simple regime detection:

Bull, Bear, Sideways, High Vol

Configuration (UI)
Tickers: AAPL, MSFT, GOOGL

Period: 1mo, 3mo, 6mo, 1y, 2y

Weights: equal or custom

Rebalancing: none, monthly, quarterly

Benchmark: e.g. SPY, QQQ, ^GSPC

Metrics (short)
Sharpe: excess return / volatility

Sortino: uses downside volatility only

Calmar: CAGR / max drawdown

VaR 95%: loss threshold at 95% confidence

CVaR 95%: expected loss beyond VaR

Hurst:

0.5: trending

≈ 0.5: random walk

< 0.5: mean-reverting
