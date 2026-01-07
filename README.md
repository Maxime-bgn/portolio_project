# Quant B - Portfolio Analytics Dashboard

Multi-asset portfolio management platform with advanced risk analytics.

## Structure

```
quant_b_final/
├── app.py                          # Main application (multi-page)
├── portfolio_module/
│   ├── __init__.py
│   ├── portfolio_core.py           # Core metrics (Sharpe, Sortino, VaR, etc.)
│   ├── components.py               # UI components (professional design)
│   └── advanced_analytics.py       # Hurst, multi-scale variance, regimes
└── utils/
    ├── __init__.py
    ├── data_fetcher.py             # Yahoo Finance data retrieval
    └── daily_report.py             # Daily report generator (cron)
```

## Installation

```bash
# Install dependencies
pip install dash dash-bootstrap-components plotly pandas numpy yfinance scipy

# Run the app
python3 app.py
```

Open browser at: http://localhost:8050

## Features

### Page 1: PORTFOLIO
- Real-time price cards
- Performance chart (base 100)
- Allocation pie chart
- Drawdown analysis
- Correlation matrix
- Portfolio metrics: Sharpe, Sortino, Calmar, VaR, CVaR, etc.
- Asset breakdown table

### Page 2: ADVANCED ANALYTICS
- Hurst Exponent by asset (persistence analysis)
- Multi-scale variance (volatility at different time scales)
- Variance Ratio Test (Lo-MacKinlay random walk test)
- Regime Detection (Bull/Bear/High Vol/Sideways)

## Configuration

- **Assets**: Enter tickers separated by commas (e.g., AAPL, MSFT, GOOGL)
- **Period**: 1mo, 3mo, 6mo, 1y, 2y
- **Weights**: Equal or Custom
- **Rebalancing**: Never, Monthly, Quarterly
- **Benchmark**: For Beta/Alpha calculation (e.g., SPY)

## Metrics Explanation

**Sharpe Ratio**: Return / Volatility (>1 = good, >2 = excellent)
**Sortino Ratio**: Like Sharpe but only penalizes downside
**Calmar Ratio**: CAGR / Max Drawdown
**VaR 95%**: Maximum loss with 95% confidence
**CVaR 95%**: Expected loss beyond VaR (Expected Shortfall)
**Hurst Exponent**: H>0.5 = persistent, H=0.5 = random walk, H<0.5 = mean-reverting

## Daily Report

Configure cron job to generate daily reports:

```bash
# Edit crontab
crontab -e

# Add line (runs at 8pm daily)
0 20 * * * cd /path/to/project && python3 utils/daily_report.py
```

## Auto-refresh

Dashboard auto-refreshes every 5 minutes for live data.

## Notes

Based on ESILV Market Risk course 2024-2025.
All advanced analytics (Hurst, multi-scale variance) follow course methodology.
