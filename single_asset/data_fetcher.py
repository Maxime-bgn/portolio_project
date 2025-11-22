
import yfinance as yf
import pandas as pd

TICKER = "GLE.PA"


def fetch_data(period: str = "1y") -> pd.DataFrame:
    
    asset = yf.Ticker(TICKER)
    df = asset.history(period=period)
    return df


def get_current_price() -> dict:
    
    asset = yf.Ticker(TICKER)
    info = asset.info
    hist = asset.history(period="2d")
    
    # Calcul variation journalière
    if len(hist) >= 2:
        prev_close = hist["Close"].iloc[-2]
        curr_close = hist["Close"].iloc[-1]
        change_pct = ((curr_close - prev_close) / prev_close) * 100
    else:
        change_pct = 0
    
    return {
        "price": info.get("regularMarketPrice") or hist["Close"].iloc[-1],
        "change": change_pct,
        "name": info.get("shortName", TICKER),
        "currency": info.get("currency", "EUR")
    }