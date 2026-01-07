import yfinance as yf
import pandas as pd


def fetch_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch historical data for the selected asset.
    
    Args:
        ticker: Asset symbol (e.g., "AAPL", "BTC-USD", "GLE.PA", "^FCHI")
        period: Time period (e.g., "1mo", "6mo", "1y", "2y", "5y", "max")
    
    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume
    """
    asset = yf.Ticker(ticker)
    df = asset.history(period=period)
    return df


def get_current_price(ticker: str) -> dict:
    """
    Fetch current price and info for the selected asset.
    
    Args:
        ticker: Asset symbol
    
    Returns:
        dict with: ticker, price, change, name, currency, exchange
    """
    asset = yf.Ticker(ticker)
    info = asset.info
    hist = asset.history(period="2d")
    
    # Calculate daily change
    if len(hist) >= 2:
        prev_close = hist["Close"].iloc[-2]
        curr_close = hist["Close"].iloc[-1]
        change_pct = ((curr_close - prev_close) / prev_close) * 100
    else:
        change_pct = 0
    
    return {
        "ticker": ticker,
        "price": info.get("regularMarketPrice") or hist["Close"].iloc[-1],
        "change": change_pct,
        "name": info.get("shortName", ticker),
        "currency": info.get("currency", "USD"),
        "exchange": info.get("exchange", "N/A")
    }


