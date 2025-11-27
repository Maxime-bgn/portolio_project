# Portfolio Project

A univariate backtesting engine for testing quantitative trading strategies on single assets. This project includes data retrieval, signal generation, portfolio simulation, and performance metrics calculation.

---

## Features

- **Automated Market Data Retrieval** — Fetch historical price data seamlessly
- **Signal Construction** — Built-in support for momentum, breakout, moving averages, and more
- **Position Generation** — Automatic trade signal conversion to portfolio positions
- **PnL Simulation & Equity Curve** — Track portfolio value over time
- **Performance Metrics** — Calculate Sharpe ratio, maximum drawdown, annualized volatility, and CAGR
- **Modular Architecture** — Clean separation between utilities, core logic, and components

---

## Project Structure
```
portfolio_project/
│
├── app.py                      # Main execution script
├── portfolio_module/
│   ├── portfolio_core.py       # Backtesting engine logic
│   └── components.py           # Generic utility functions
├── utils/
│   ├── data_fetcher.py         # Data management and retrieval
│   └── __init__.py
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## Installation

Clone the repository:
```bash
git clone https://github.com/username/portfolio_project.git
cd portfolio_project
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage

### Run the Main Script

Execute the complete backtesting workflow with predefined parameters:
```bash
python app.py
```

This script runs a full backtest using the configuration defined in `app.py`.

---

## Customization

Modify backtesting parameters in the following files:

- **`app.py`** — Main execution parameters
- **`portfolio_module/portfolio_core.py`** — Core backtesting engine logic
- **`utils/data_fetcher.py`** — Data source configuration

---

## Roadmap

Future enhancements planned for this project:

- Multi-asset portfolio support
- Streamlit web interface
- Automated hyperparameter optimization
- Transaction costs and slippage modeling

---

## License

This project is open source and available under the MIT License.

---

## Contributing

Contributions are welcome. Please open an issue or submit a pull request for any improvements or bug fixes.