# portolio_project

Collection of two Streamlit dashboards:
1) Single Asset Strategy Testing  
2) Multi-Asset Portfolio Analytics

---

## Single Asset Strategy Dashboard (Streamlit)

Interactive dashboard to test and compare systematic strategies on a single ticker.

### Overview
Fetch and visualise price data

Backtest rule-based strategies

Evaluate cumulative performance and drawdowns

Benchmark against Buy & Hold

shell
Copy code

### Structure
single_asset/
├── data_fetcher.py # Retrieve historical prices
├── strategies.py # Trading strategy implementations
├── charts.py # Plotting functions
├── metrics.py # Performance metrics (Sharpe, DD, etc.)
└── app.py # Streamlit frontend

shell
Copy code

### Installation
pip install streamlit pandas numpy yfinance plotly
streamlit run single_asset/app.py

shell
Copy code

### Default URL
http://localhost:8501

shell
Copy code

### Included Strategies
Buy & Hold
End-of-Month
Volatility Breakout
Trend Following
Golden Cross
RSI Oversold
MACD Crossover

shell
Copy code

### Metrics
Total return / Annualised return
Volatility
Sharpe ratio
Max drawdown
Recovery time

shell
Copy code

### Notes
Designed for strategy testing and educational purposes.

yaml
Copy code

---

## Quant B – Multi-Asset Portfolio Dashboard

Multi-asset portfolio analytics platform with performance, allocation, and risk diagnostics.

### Overview
Build and analyse portfolios

Compute risk/return statistics

Explore drawdowns and correlations

Run advanced analytics (Hurst, regime detection)

shell
Copy code

### Structure
FinalApp.py # Main Streamlit interface
portfolio_module/
├── portfolio_core.py # Core risk/return metrics
├── advanced_analytics.py # Hurst, variance ratio, regimes
└── components.py # UI + charts
utils/
└── data_fetcher.py # Yahoo Finance data
reports/ # Optional generated reports

shell
Copy code

### Installation
pip install streamlit pandas numpy yfinance plotly scipy
streamlit run FinalApp.py

shell
Copy code

### Default URL
http://localhost:8501

shell
Copy code

### Features
Performance (base 100)
Allocation by asset
Drawdown curve + statistics
Correlation matrix

shell
Copy code

### Metrics
Annualised return/volatility
Sharpe, Sortino, Calmar
Max drawdown
VaR, CVaR
Beta/Alpha vs benchmark

shell
Copy code

### Advanced analytics
Hurst exponent
Multi-timeframe variance
Variance Ratio test
Bull / Bear / Sideways / High Volatility regimes

Copy code
