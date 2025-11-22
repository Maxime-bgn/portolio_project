# 📈 Portfolio Dashboard

A real-time financial dashboard for quantitative portfolio analysis, built with Python and Dash.

## 🎯 Features

- **Real-time Data**: Fetches live market data from Yahoo Finance API
- **Multi-Asset Support**: Track stocks, crypto, forex, and more
- **Auto-Refresh**: Data updates automatically every 5 minutes
- **Interactive Charts**: Plotly-powered visualizations with zoom, pan, hover
- **Daily Reports**: Automated daily reports via cron job
- **Portfolio Analysis**: Performance metrics, correlation, volatility

## 🏗️ Project Structure

```
portfolio_project/
├── app.py                 # Main Dash application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── utils/
│   ├── __init__.py
│   └── data_fetcher.py   # Yahoo Finance API utilities
├── quant_a/              # Single Asset Analysis Module
│   └── ...
├── quant_b/              # Portfolio Analysis Module
│   └── ...
├── cron/
│   ├── daily_report.py   # Daily report generator
│   └── README.md         # Cron setup documentation
└── reports/              # Generated daily reports
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Maxime-bgn/portolio_project.git
cd portolio_project

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open your browser at: **http://localhost:8050**

## 📊 Usage

### Changing Assets

Enter ticker symbols separated by commas:
- Stocks: `AAPL`, `MSFT`, `GOOGL`
- Crypto: `BTC-USD`, `ETH-USD`
- Forex: `EURUSD=X`, `GBPUSD=X`
- French stocks: `ENGI.PA`, `MC.PA`

### Time Period

Select from: 1 Month, 3 Months, 6 Months, 1 Year, 2 Years

## ⏰ Cron Job Setup

Daily reports are generated automatically at 8pm. See [cron/README.md](cron/README.md) for setup instructions.

```bash
# Add to crontab
0 20 * * * cd /path/to/portfolio_project && python3 cron/daily_report.py
```

## 🖥️ Deployment (Linux VM)

### Using systemd (recommended for 24/7)

1. Create service file:
```bash
sudo nano /etc/systemd/system/portfolio.service
```

2. Add configuration:
```ini
[Unit]
Description=Portfolio Dashboard
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/portfolio_project
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl enable portfolio
sudo systemctl start portfolio
```

### Using screen (simple)

```bash
screen -S portfolio
python app.py
# Press Ctrl+A, then D to detach
```

## 👥 Team

| Role | Module | Description |
|------|--------|-------------|
| **Quant A** | Single Asset | Backtesting, strategies, predictions |
| **Quant B** | Portfolio | Multi-asset, correlations, optimization |

## 📦 Dependencies

- **dash** - Web framework
- **plotly** - Interactive charts
- **pandas** - Data manipulation
- **yfinance** - Yahoo Finance API
- **numpy** - Numerical computations

## 📝 License

Educational project - ESILV Paris
