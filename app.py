""""
Unified Quant Dashboard - Streamlit Version
Single Asset Only
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "portolio_project-main"))

# Single Asset imports only
from single_asset.data_fetcher import fetch_data, get_current_price
from single_asset.strategies import (
    buy_and_hold, macd_crossover, end_of_month, volatility_breakout,
    trend_following, golden_cross, rsi_oversold, linear_regression_strategy
)
from single_asset.metrics import get_all_metrics
from single_asset.charts import (
    plot_strategy_normalized, 
    plot_drawdown,
    plot_returns_distribution
)

# Minimal color palette for UI
COLORS = {
    "background": "#111111",
    "card": "#1a1a1a",
    "border": "#292929",
    "text": "#FFFFFF",
    "text_secondary": "#777777",

    # Accent & status
    "accent": "#00d4ff",
    "positive": "#00ff88",
    "negative": "#ff6b6b",
    "warning": "#ffd93d",
    "info": "#9d4edd",

    # Direct chart colors
    "blue": "#00d4ff",
    "green": "#00ff88",
    "orange": "#ffa500",
    "red": "#ff0000"
}

# Page config
st.set_page_config(
    page_title="Quant Dashboard | Single Asset",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SINGLE ASSET MODULE

def render_quant_a():
    """Single-Asset Backtester"""

    st.markdown(f"""
    <div style="padding-bottom:16px;">
        <h1 style="color:{COLORS['text']};font-weight:700;font-size:28px;">
            QUANT A - SINGLE ASSET STRATEGY BACKTESTER
        </h1>
        <p style="color:{COLORS['text_secondary']};font-size:14px;">
            Backtest systematic trading strategies on a single ticker.
        </p>
        <p style="color:{COLORS['positive']};font-size:11px;font-weight:500;">
            Updated: {datetime.now().strftime('%H:%M:%S')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # User config
    st.markdown(f'<div style="background:{COLORS["card"]};padding:18px;border-radius:8px;">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        ticker = st.text_input("Ticker", value="GLE.PA").upper()

    with col2:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

    with col3:
        strategy = st.selectbox(
            "Strategy",
            [
                "Buy & Hold",
                "MACD Crossover",
                "Trend Following",
                "Golden Cross",
                "RSI Oversold",
                "End of Month",
                "Volatility Breakout",
                "Linear Regression"
            ]
        )

    with col4:
        initial_capital = st.number_input("Initial Capital (€)", min_value=1000, max_value=1_000_000, value=10000, step=1000)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Data
    try:
        data = fetch_data(ticker, period)
        if data.empty:
            st.error(f"Could not fetch data for {ticker}")
            return

        current_info = get_current_price(ticker)

        # Price card
        col1, col2, col3, col4 = st.columns(4)
        is_positive = current_info["change"] >= 0
        change_color = COLORS["positive"] if is_positive else COLORS["negative"]
        arrow = "▲" if is_positive else "▼"

        with col1:
            st.metric(
                ticker,
                f"{current_info['price']:.2f} {current_info['currency']}",
                f"{arrow}{current_info['change']:.2f}%"
            )
        with col2:
            st.metric("NAME", current_info['name'])
        with col3:
            st.metric("EXCHANGE", current_info['exchange'])
        with col4:
            st.metric("CURRENCY", current_info['currency'])

        # Strategy exec
        strategy_funcs = {
            "Buy & Hold": buy_and_hold,
            "MACD Crossover": macd_crossover,
            "Trend Following": trend_following,
            "Golden Cross": golden_cross,
            "RSI Oversold": rsi_oversold,
            "End of Month": end_of_month,
            "Volatility Breakout": volatility_breakout,
            "Linear Regression": linear_regression_strategy
        }

        result = strategy_funcs[strategy](data, initial_capital=initial_capital)
        metrics = get_all_metrics(result)

        # Main chart
        st.subheader(f"Performance: {strategy}")
        fig = plot_strategy_normalized(data, result, ticker, strategy, colors=COLORS)
        st.plotly_chart(fig, use_container_width=True)

        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Return (%)", f"{metrics['Total Return (%)']}%")
        col2.metric("Sharpe Ratio", metrics["Sharpe Ratio"])
        col3.metric("Max Drawdown (%)", f"{metrics['Max Drawdown (%)']}%")
        col4.metric("Win Rate (%)", f"{metrics['Win Rate (%)']}%")

        # Secondary charts
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Drawdown")
            st.plotly_chart(plot_drawdown(result), use_container_width=True)
        with col2:
            st.subheader("Return Distribution")
            st.plotly_chart(plot_returns_distribution(result), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")


def main():
    render_quant_a()

    st.markdown("""
    <div style="text-align:center;color:#888;font-size:11px;margin-top:28px;">
        Single-Asset Version — Multi-Asset Module Disabled
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
