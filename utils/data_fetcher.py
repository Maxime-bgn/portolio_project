"""
Data fetching utilities - Yahoo Finance API
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict


def fetch_asset_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a single asset.
    
    Args:
        ticker: Symbol (e.g., 'AAPL', 'ENGI.PA', 'BTC-USD', 'EURUSD=X')
        period: '1mo', '3mo', '6mo', '1y', '2y', '5y'
    
    Returns:
        DataFrame with Date index and OHLCV columns
    """
    try:
        asset = yf.Ticker(ticker)
        df = asset.history(period=period)
        if df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.DataFrame()


def fetch_multiple_assets(tickers: List[str], period: str = "1y") -> pd.DataFrame:
    """
    Fetch closing prices for multiple assets.
    
    Returns:
        DataFrame with Date index and ticker columns
    """
    data = {}
    for ticker in tickers:
        df = fetch_asset_data(ticker, period)
        if not df.empty:
            data[ticker] = df["Close"]
    
    if not data:
        return pd.DataFrame()
    
    return pd.DataFrame(data).dropna()


def get_current_prices(tickers: List[str]) -> Dict[str, dict]:
    """
    Get real-time prices and info for multiple assets.
    
    Returns:
        Dict with ticker as key and info dict as value
    """
    results = {}
    for ticker in tickers:
        try:
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
            
            results[ticker] = {
                "price": info.get("regularMarketPrice") or (hist["Close"].iloc[-1] if not hist.empty else 0),
                "change": change_pct,
                "name": info.get("shortName", ticker),
                "currency": info.get("currency", "USD")
            }
        except Exception as e:
            print(f"Error getting price for {ticker}: {e}")
            results[ticker] = {
                "price": 0,
                "change": 0,
                "name": ticker,
                "currency": "USD"
            }
    
    return results
