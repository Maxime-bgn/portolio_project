# Portfolio Project — Streamlit Backtesting App

A single-asset backtesting engine operated through an interactive Streamlit dashboard.  
The app retrieves market data, generates trading signals, simulates portfolio evolution, and visualizes results directly in the browser.

## Features

- Automated market data retrieval from online sources
- Built-in trading strategies (trend following, momentum, breakout, RSI, MACD, etc.)
- Position and PnL simulation using compounded returns
- Equity curve and normalized performance comparison
- Standard performance metrics:
  - Annualized return
  - Sharpe ratio
  - Maximum drawdown
  - Win rate and profit factor
- Interactive visualization using Streamlit and Plotly
- Modular and extensible code structure

## Project Structure

portfolio_project/
│
├── app.py # Streamlit user interface and workflow
├── single_asset/
│ ├── strategies.py # Strategy rule definitions
│ ├── charts.py # Plotting utilities (Plotly)
│ ├── metrics.py # Performance statistics
│ ├── data_fetcher.py # Data download and cleaning
│ └── ...
├── utils/
│ └── data_fetcher.py # Shared data access helpers
├── requirements.txt # Python dependencies
└── README.md # Documentation


shell
Copy code

## Installation

Clone the repository:
git clone https://github.com/username/portfolio_project.git
cd portfolio_project

csharp
Copy code

Install required packages:
pip install -r requirements.txt

shell
Copy code

## Usage

Run the Streamlit dashboard:
streamlit run app.py

markdown
Copy code

From the interface you can:
- Select an asset ticker
- Choose the strategy to run
- Visualize price series, equity curve, and drawdowns
- Inspect performance statistics

No scripting required for basic operation.

## Customization

Modify functionality as needed:
- `single_asset/strategies.py` — Add or tune trading strategies
- `single_asset/metrics.py` — Extend performance measurements
- `single_asset/charts.py` — Customize plots and layout
- `single_asset/data_fetcher.py` — Change data source or API logic
- `app.py` — Add dashboard controls or application flow

## Roadmap

Planned future additions:
- Multi-asset portfolios
- Hyperparameter optimization
- Support for transaction costs and slippage
- Optional deployment templates for cloud hosting
