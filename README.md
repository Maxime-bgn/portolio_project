Here's a clean, professional README in pure Markdown format suitable for a GitHub repository:
markdown# Quantitative Finance Dashboards

Two interactive applications built with Streamlit for quantitative analysis and portfolio management.

---

## 1. Single Asset Strategy Dashboard

Backtesting platform for systematic trading strategies on individual securities.

### Features

- **Fetch & Visualize**: Historical data retrieval and price visualization
- **Backtesting**: Test strategies based on defined trading rules
- **Performance**: Evaluation of cumulative returns and drawdowns
- **Benchmark**: Systematic comparison against Buy & Hold strategy

### Integrated Strategies

- Buy & Hold
- End-of-Month & Volatility Breakout
- Trend Following (Golden Cross, MACD Crossover)
- RSI Oversold

### Calculated Metrics

- Total and annualized returns
- Volatility and Sharpe Ratio
- Maximum Drawdown and recovery time

### Module Structure
```
single_asset/
├── data_fetcher.py  # Historical price retrieval
├── strategies.py    # Trading rule implementation
├── charts.py        # Visualization functions
├── metrics.py       # Performance calculations
└── app.py           # Streamlit interface
```

### Launch
```bash
pip install streamlit pandas numpy yfinance plotly
streamlit run single_asset/app.py
```

---

## 2. Quant B – Multi-Asset Portfolio Dashboard

Multi-asset portfolio analysis platform with advanced risk diagnostics.

### Features

- **Portfolio Analytics**: Risk and return statistics calculation
- **Allocation**: Asset distribution visualization
- **Risk Management**: Correlation analysis, VaR (Value at Risk), and CVaR
- **Advanced Analytics**: Hurst exponent, Variance Ratio, and regime detection

### Detected Market Regimes

- Bull / Bear
- Sideways (Lateral)
- High Volatility

### Advanced Metrics

- Ratios: Sharpe, Sortino, Calmar
- Alpha and Beta relative to benchmark
- Correlation matrix

### Module Structure
```
FinalApp.py              # Main interface
portfolio_module/
├── portfolio_core.py    # Core metrics
├── advanced_analytics.py # Hurst, variance ratio, regimes
└── components.py        # UI components
utils/
└── data_fetcher.py      # Yahoo Finance data management
```

### Launch
```bash
pip install streamlit pandas numpy yfinance plotly scipy
streamlit run FinalApp.py
```

---

## Technical Stack

- **Language**: Python
- **Interface**: Streamlit
- **Data Analysis**: Pandas, NumPy, SciPy
- **Visualization**: Plotly
- **Data Source**: Yahoo Finance API
