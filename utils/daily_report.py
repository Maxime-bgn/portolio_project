#!/usr/bin/env python3
"""
Daily Report Generator
Genere un rapport journalier avec les metriques cles.
Cron: 0 20 * * * python3 daily_report.py
"""

from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf

# Config
ASSETS = ["AAPL", "MSFT", "GOOGL", "BTC-USD"]
SCRIPT_DIR = Path(__file__).parent
REPORTS_DIR = SCRIPT_DIR.parent / "reports"

def fetch_data(ticker, period="3mo"):
    """Recupere les donnees historiques."""
    try:
        asset = yf.Ticker(ticker)
        df = asset.history(period=period)
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.DataFrame()


def calculate_volatility(df, window=30):
    """Calcule la volatilite annualisee."""
    if df.empty or len(df) < window:
        return 0.0
    returns = df["Close"].pct_change().dropna()
    volatility = returns.tail(window).std() * np.sqrt(252) * 100
    return volatility


def calculate_max_drawdown(df):
    """Calcule le drawdown maximum."""
    if df.empty:
        return 0.0
    prices = df["Close"]
    rolling_max = prices.expanding().max()
    drawdown = (prices - rolling_max) / rolling_max
    return drawdown.min() * 100


def generate_asset_report(ticker):
    """Genere le rapport pour un asset."""
    df = fetch_data(ticker)
    
    if df.empty:
        return {
            "ticker": ticker,
            "error": "No data available"
        }
    
    today = df.iloc[-1]
    yesterday = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
    
    daily_change = ((today["Close"] - yesterday["Close"]) / yesterday["Close"]) * 100
    
    return {
        "ticker": ticker,
        "date": df.index[-1].strftime("%Y-%m-%d"),
        "open": round(today["Open"], 2),
        "close": round(today["Close"], 2),
        "high": round(today["High"], 2),
        "low": round(today["Low"], 2),
        "volume": int(today["Volume"]),
        "daily_change_pct": round(daily_change, 2),
        "volatility_30d_pct": round(calculate_volatility(df), 2),
        "max_drawdown_pct": round(calculate_max_drawdown(df), 2)
    }


def generate_full_report(assets):
    """Genere le rapport complet."""
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append(f"DAILY PORTFOLIO REPORT")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 60)
    report_lines.append("")
    
    for ticker in assets:
        data = generate_asset_report(ticker)
        
        if "error" in data:
            report_lines.append(f"[{ticker}] ERROR: {data['error']}")
            report_lines.append("")
            continue
        
        report_lines.append(f"[{data['ticker']}] - {data['date']}")
        report_lines.append("-" * 40)
        report_lines.append(f"  Open:           {data['open']:>12}")
        report_lines.append(f"  Close:          {data['close']:>12}")
        report_lines.append(f"  High:           {data['high']:>12}")
        report_lines.append(f"  Low:            {data['low']:>12}")
        report_lines.append(f"  Volume:         {data['volume']:>12,}")
        report_lines.append(f"  Daily Change:   {data['daily_change_pct']:>11}%")
        report_lines.append(f"  Volatility(30d):{data['volatility_30d_pct']:>11}%")
        report_lines.append(f"  Max Drawdown:   {data['max_drawdown_pct']:>11}%")
        report_lines.append("")
    
    report_lines.append("=" * 60)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 60)
    
    return "\n".join(report_lines)


def save_report(report):
    """Sauvegarde le rapport."""
    # Create reports directory if it doesn't exist
    REPORTS_DIR.mkdir(exist_ok=True)
    
    # Generate filename with date
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = REPORTS_DIR / filename
    
    with open(filepath, "w") as f:
        f.write(report)
    
    return str(filepath)


if __name__ == "__main__":
    print(f"Generating report for: {', '.join(ASSETS)}")
    
    report = generate_full_report(ASSETS)
    print(report)
    
    filepath = save_report(report)
    print(f"\nSaved to: {filepath}")
