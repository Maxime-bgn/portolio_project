import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "single_asset"))

from single_asset.data_fetcher import fetch_data, get_current_price
from single_asset.charts import plot_strategy_normalized
from single_asset.strategies import (
    buy_and_hold, end_of_month, volatility_breakout,
    trend_following, golden_cross, rsi_oversold, macd_crossover
)
from single_asset.metrics import get_all_metrics

from utils.data_fetcher import fetch_multiple_assets as fetch_multiple_assets_pm
from utils.data_fetcher import get_current_prices as get_current_prices_pm
from portfolio_module import portfolio_core as pm_core
from portfolio_module.ml_advanced_analysis import ml_advanced_analysis
from portfolio_module import components as pm_components
from portfolio_module.advanced_analytics import (
    estimate_hurst_exponent, multi_scale_variance,
    detect_regimes_simple, variance_ratio_test
)

DEFAULT_PORTFOLIO_ASSETS = ["AAPL", "MSFT", "GOOGL", "XLF", "GLD"]

st.set_page_config(
    page_title="Quant Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    .main-header {
        border-bottom: 1px solid #333333;
        padding: 24px 0;
        margin-bottom: 24px;
    }
    
    .portfolio-card {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 20px;
        border: 1px solid #333333;
        margin-bottom: 20px;
    }
    
    .price-card {
        background-color: #1a1a1a;
        border-radius: 6px;
        padding: 15px;
        border: 1px solid #333333;
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .metric-card {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
        margin-bottom: 10px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #000000;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #000000;
        color: #ffffff;
        border-radius: 4px 4px 0 0;
        padding: 10px 24px;
        font-weight: 500;
        font-size: 14px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1a1a1a;
        font-weight: 600;
        border-bottom: 2px solid #0066cc;
    }
    
    .section-title {
        color: #ffffff;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    
    .stButton>button {
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 4px;
    }
    
    .stButton>button:hover {
        background-color: #0052a3;
    }
    
    .stSelectbox, .stTextInput > div > div > input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border-color: #333333 !important;
    }
    
    .footer {
        text-align: center;
        color: #8b949e;
        font-size: 11px;
        opacity: 0.7;
        margin-top: 32px;
        padding-top: 24px;
        border-top: 1px solid #333333;
    }
</style>
""", unsafe_allow_html=True)

if "current_ticker" not in st.session_state:
    st.session_state.current_ticker = "GLE.PA"
if "portfolio_weights" not in st.session_state:
    st.session_state.portfolio_weights = {}
if "current_page_b" not in st.session_state:
    st.session_state.current_page_b = "portfolio"

STRATEGIES = {
    "Buy and Hold": buy_and_hold,
    "Volatility Breakout": volatility_breakout,
    "Trend Following": trend_following,
    "Golden Cross": golden_cross,
    "RSI Oversold": rsi_oversold,
    "End of Month": end_of_month,
    "MACD Crossover": macd_crossover
}

COLORS = {
    "background": "#0a0a0a",
    "card": "#1a1a1a",
    "text": "#ffffff",
    "text_secondary": "#8b949e",
    "blue": "#00d4ff",
    "green": "#00ff88",
    "red": "#ff4444",
    "orange": "#ffa500",
    "purple": "#9d4edd",
    "border": "#333333",
    "positive": "#00ff88",
    "negative": "#ff4444",
    "warning": "#ffa500",
    "accent": "#00d4ff",
    "info": "#9d4edd"
}

def main():
    st.markdown("""
    <div class="main-header">
        <h1 style="color: """ + COLORS["text"] + """; font-weight: 700; font-size: 28px; margin-bottom: 4px; letter-spacing: -0.5px;">
            QUANT DASHBOARD
        </h1>
        <p style="color: """ + COLORS["text_secondary"] + """; font-size: 14px; margin-bottom: 8px;">
            Multi-Asset Analysis & Portfolio Management
        </p>
        <p style="color: """ + COLORS["positive"] + """; font-size: 11px; font-weight: 500;">
            Last update: """ + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + """
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_quant_a, tab_quant_b = st.tabs(["Quant A - Single Asset", "Quant B - Portfolio & Advanced Analytics"])
    
    with tab_quant_a:
        quant_a_dashboard()
    
    with tab_quant_b:
        quant_b_dashboard()

def quant_a_dashboard():
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        st.markdown("### Asset")
        ticker_input = st.text_input("Ticker", value=st.session_state.current_ticker, label_visibility="collapsed")
        
        col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
        with col_btn1:
            if st.button("GLE.PA", use_container_width=True):
                st.session_state.current_ticker = "GLE.PA"
        with col_btn2:
            if st.button("AAPL", use_container_width=True):
                st.session_state.current_ticker = "AAPL"
        with col_btn3:
            if st.button("BTC-USD", use_container_width=True):
                st.session_state.current_ticker = "BTC-USD"
        with col_btn4:
            if st.button("TSLA", use_container_width=True):
                st.session_state.current_ticker = "TSLA"
        with col_btn5:
            if st.button("SPY", use_container_width=True):
                st.session_state.current_ticker = "SPY"
        
        if ticker_input != st.session_state.current_ticker:
            st.session_state.current_ticker = ticker_input.upper().strip()
    
    ticker = st.session_state.current_ticker
    
    try:
        info = get_current_price(ticker)
        
        with col2:
            st.markdown("### Current Price")
            is_positive = info["change"] >= 0
            color = COLORS["green"] if is_positive else COLORS["red"]
            arrow = "▲" if is_positive else "▼"
            
            st.markdown("<h2 style='color: #ffffff; margin: 0;'>{0:.2f} {1}</h2>".format(info["price"], info["currency"]), unsafe_allow_html=True)
            st.markdown("<h3 style='color: " + color + "; font-weight: bold; margin-top: 5px;'>" + arrow + " {0:+.2f}%</h3>".format(info["change"]), unsafe_allow_html=True)
        
        with col3:
            st.markdown("### Information")
            st.markdown("**Name:** " + info["name"])
            st.markdown("**Ticker:** " + info["ticker"])
            st.markdown("**Exchange:** " + info["exchange"])
            
    except Exception as e:
        with col2:
            st.error("Error: " + str(e))
        with col3:
            st.error("Unable to load " + ticker)
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        period = st.selectbox(
            "Period",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            format_func=lambda x: {"1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months", "1y": "1 Year", "2y": "2 Years", "5y": "5 Years"}[x],
            index=3,
            key="quant_a_period"
        )
    
    with col2:
        strategy_name = st.selectbox("Strategy", options=list(STRATEGIES.keys()), key="quant_a_strategy")
    
    with col3:
        display_mode = st.selectbox(
            "Display",
            options=["base100", "returns"],
            format_func=lambda x: "Base 100 (Performance)" if x == "base100" else "Cumulative Returns %",
            key="quant_a_display"
        )
    
    with col4:
        capital = st.number_input("Initial Capital", value=10000, step=1000, key="quant_a_capital")
    
    try:
        data = fetch_data(ticker, period)
        strategy_func = STRATEGIES[strategy_name]
        result = strategy_func(data, initial_capital=capital)
        
        col_chart, col_metrics = st.columns([2, 1])
        
        with col_chart:
            st.markdown("### " + ticker + " - " + strategy_name)
            fig = plot_strategy_normalized(data, result, ticker, strategy_name, COLORS, display_mode)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_metrics:
            st.markdown("### Performance")
            metrics = get_all_metrics(result)
            
            for name, value in metrics.items():
                if "Return" in name:
                    try:
                        val = float(str(value).replace("%", "").replace(",", "."))
                        color = COLORS["green"] if val >= 0 else COLORS["red"]
                    except:
                        color = COLORS["blue"]
                elif "Drawdown" in name:
                    color = COLORS["red"]
                elif "Sharpe" in name or "Calmar" in name:
                    try:
                        val = float(value)
                        if val >= 2:
                            color = COLORS["green"]
                        elif val >= 1:
                            color = COLORS["orange"]
                        else:
                            color = COLORS["red"]
                    except:
                        color = COLORS["blue"]
                else:
                    color = COLORS["blue"]
                
                st.markdown("""
                <div class='metric-card'>
                    <p style='color: #ffffff; opacity: 0.7; font-size: 12px; margin: 0;'>""" + name + """</p>
                    <h4 style='color: """ + color + """; margin: 3px 0; font-weight: bold; font-size: 18px;'>""" + str(value) + """</h4>
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error("Error loading data: " + str(e))
    
    st.markdown("""
    <div class='footer'>
        <p>
            <span style="margin-right: 20px;">Auto-refresh: 5 minutes</span>
            <span style="margin-right: 20px; opacity: 0.3;">•</span>
            <span style="margin-right: 20px;">Quant A Module</span>
            <span style="margin-right: 20px; opacity: 0.3;">•</span>
            <span>Single Asset Backtesting</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

def quant_b_dashboard():
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button("PORTFOLIO", use_container_width=True):
            st.session_state.current_page_b = "portfolio"
            st.rerun()
    with col_nav2:
        if st.button("ADVANCED ANALYTICS", use_container_width=True):
            st.session_state.current_page_b = "advanced"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.current_page_b == "portfolio":
        portfolio_page()
    else:
        advanced_analytics_page()

def portfolio_page():
    with st.container():
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            assets_input = st.text_input(
                "Assets (tickers)",
                value=", ".join(pm_core.DEFAULT_ASSETS),
                help="Separate with commas: AAPL, GOOGL, MSFT",
                key="portfolio_assets"
            )
        
        with col2:
            period = st.selectbox(
                "Period",
                options=["1mo", "3mo", "6mo", "1y", "2y"],
                index=3,
                format_func=lambda x: {
                    "1mo": "1 Month",
                    "3mo": "3 Months", 
                    "6mo": "6 Months",
                    "1y": "1 Year",
                    "2y": "2 Years"
                }[x],
                key="portfolio_period"
            )
        
        with col3:
            weight_mode = st.selectbox(
                "Weight Mode",
                options=["equal", "custom"],
                index=0,
                format_func=lambda x: {
                    "equal": "Equal",
                    "custom": "Custom"
                }[x],
                key="portfolio_weight_mode"
            )
        
        with col4:
            rebalancing = st.selectbox(
                "Rebalancing",
                options=["never", "monthly", "quarterly"],
                index=0,
                format_func=lambda x: {
                    "never": "Never",
                    "monthly": "Monthly",
                    "quarterly": "Quarterly"
                }[x],
                key="portfolio_rebalancing"
            )
        
        with col5:
            benchmark = st.text_input(
                "Benchmark",
                value="SPY",
                placeholder="Ex: SPY",
                key="portfolio_benchmark"
            )
        
        if weight_mode == "custom":
            weights_input = st.text_input(
                "Custom Weights (%)",
                value="20, 20, 20, 20, 20",
                placeholder="Ex: 30, 25, 20, 15, 10",
                key="portfolio_custom_weights"
            )
        else:
            weights_input = ""
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    assets = [a.strip().upper() for a in assets_input.split(",") if a.strip()]
    
    if not assets:
        st.warning("Please enter at least one ticker")
        return
    
    df = fetch_multiple_assets_pm(assets, period)
    
    if df.empty:
        st.error("Unable to fetch data. Check tickers.")
        return
    
    if weight_mode == "equal":
        weights = pm_core.create_equal_weights(df.columns.tolist())
    else:
        try:
            weight_values = [float(w.strip()) for w in weights_input.split(",")]
            if len(weight_values) != len(df.columns):
                weight_values = [100 / len(df.columns)] * len(df.columns)
        except:
            weight_values = [100 / len(df.columns)] * len(df.columns)
        
        total = sum(weight_values)
        weights = {asset: w/total for asset, w in zip(df.columns, weight_values)}
    
    market_returns = None
    if benchmark and benchmark.strip():
        try:
            benchmark_df = fetch_multiple_assets_pm([benchmark.strip().upper()], period)
            if not benchmark_df.empty:
                market_returns = pm_core.calculate_returns(benchmark_df).iloc[:, 0]
        except:
            pass
    
    prices = get_current_prices_pm(assets)
    
    cols = st.columns(len(prices))
    for idx, (ticker, info) in enumerate(prices.items()):
        with cols[idx]:
            is_positive = info["change"] >= 0
            change_color = COLORS["positive"] if is_positive else COLORS["negative"]
            arrow = "▲" if is_positive else "▼"
            
            price_formatted = "{0:.2f}".format(info["price"])
            change_formatted = "{0:.2f}".format(abs(info["change"]))
            
            st.markdown("""
            <div class="price-card">
                <div style="margin-bottom: 8px;">
                    <span style="color: """ + COLORS["accent"] + """; font-weight: 700; font-size: 11px; letter-spacing: 0.5px;">
                        """ + ticker + """
                    </span>
                </div>
                <div style="margin-bottom: 6px;">
                    <span style="color: """ + COLORS["text"] + """; font-size: 22px; font-weight: 600;">
                        $""" + price_formatted + """
                    </span>
                </div>
                <div>
                    <span style="color: """ + change_color + """; font-size: 10px; margin-right: 2px;">
                        """ + arrow + """
                    </span>
                    <span style="color: """ + change_color + """; font-weight: 600; font-size: 13px;">
                        """ + change_formatted + """%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    port_value_series = pm_core.portfolio_value(df, weights, rebalancing_freq=rebalancing)
    analysis = pm_core.analyze_portfolio(df, weights, market_returns=market_returns)
    analysis["portfolio_value"] = port_value_series
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">PERFORMANCE (BASE 100)</div>', unsafe_allow_html=True)
        
        df_norm = (df / df.iloc[0]) * 100
        main_fig = pm_components.create_main_chart(df_norm, analysis["portfolio_value"], pm_components.COLORS)
        st.plotly_chart(main_fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">ALLOCATION</div>', unsafe_allow_html=True)
        
        alloc_fig = pm_components.create_weights_pie_chart(weights)
        st.plotly_chart(alloc_fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">DRAWDOWN ANALYSIS</div>', unsafe_allow_html=True)
        
        drawdown_fig = pm_components.create_drawdown_chart(analysis["portfolio_value"])
        st.plotly_chart(drawdown_fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">CORRELATION MATRIX</div>', unsafe_allow_html=True)
        
        corr_fig = pm_components.create_correlation_heatmap(analysis["correlation"])
        st.plotly_chart(corr_fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">PORTFOLIO METRICS</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ret_val = analysis["portfolio"].get("annual_return", 0)
        ret_color = COLORS["positive"] if ret_val >= 0 else COLORS["negative"]
        st.markdown("""
        <div style="background-color: """ + COLORS["card"] + """; border-radius: 6px; padding: 15px; border: 1px solid """ + COLORS["border"] + """; height: 100%;">
            <div style="font-size: 11px; color: """ + COLORS["text_secondary"] + """; margin-bottom: 5px;">RETURN</div>
            <div style="font-size: 22px; font-weight: 600; color: """ + ret_color + """">
                """ + str(ret_val) + """%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        vol_val = analysis["portfolio"].get("volatility", 0)
        st.markdown("""
        <div style="background-color: """ + COLORS["card"] + """; border-radius: 6px; padding: 15px; border: 1px solid """ + COLORS["border"] + """; height: 100%;">
            <div style="font-size: 11px; color: """ + COLORS["text_secondary"] + """; margin-bottom: 5px;">VOLATILITY</div>
            <div style="font-size: 22px; font-weight: 600; color: """ + COLORS["warning"] + """">
                """ + str(vol_val) + """%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        sharpe_val = analysis["portfolio"].get("sharpe_ratio", 0)
        st.markdown("""
        <div style="background-color: """ + COLORS["card"] + """; border-radius: 6px; padding: 15px; border: 1px solid """ + COLORS["border"] + """; height: 100%;">
            <div style="font-size: 11px; color: """ + COLORS["text_secondary"] + """; margin-bottom: 5px;">SHARPE RATIO</div>
            <div style="font-size: 22px; font-weight: 600; color: """ + COLORS["accent"] + """">
                """ + str(sharpe_val) + """
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        dd_val = analysis["portfolio"].get("max_drawdown", 0)
        st.markdown("""
        <div style="background-color: """ + COLORS["card"] + """; border-radius: 6px; padding: 15px; border: 1px solid """ + COLORS["border"] + """; height: 100%;">
            <div style="font-size: 11px; color: """ + COLORS["text_secondary"] + """; margin-bottom: 5px;">MAX DRAWDOWN</div>
            <div style="font-size: 22px; font-weight: 600; color: """ + COLORS["negative"] + """">
                """ + str(dd_val) + """%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("See detailed metrics"):
        pm_components.create_portfolio_metrics_card(analysis["portfolio"])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ASSET BREAKDOWN</div>', unsafe_allow_html=True)
    
    asset_data = []
    for asset, metrics in analysis["assets"].items():
        asset_data.append({
            "Asset": asset,
            "Return (%)": "{0:.2f}".format(metrics["return"]),
            "Volatility (%)": "{0:.2f}".format(metrics["volatility"]),
            "Sharpe Ratio": "{0:.2f}".format(metrics["sharpe"]),
            "Weight (%)": "{0:.2f}".format(metrics["weight"])
        })
    
    df_assets = pd.DataFrame(asset_data)
    st.dataframe(df_assets, use_container_width=True, hide_index=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def advanced_analytics_page():
    with st.container():
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            assets_input = st.text_input(
                "Assets (tickers)",
                value=", ".join(pm_core.DEFAULT_ASSETS),
                help="Separate with commas: AAPL, GOOGL, MSFT",
                key="advanced_assets"
            )
        
        with col2:
            period = st.selectbox(
                "Period",
                options=["6mo", "1y", "2y", "5y"],
                index=1,
                format_func=lambda x: {
                    "6mo": "6 Months", 
                    "1y": "1 Year",
                    "2y": "2 Years",
                    "5y": "5 Years"
                }[x],
                key="advanced_period"
            )
        
        with col3:
            weight_mode = st.selectbox(
                "Weight Mode",
                options=["equal", "custom"],
                index=0,
                format_func=lambda x: {
                    "equal": "Equal",
                    "custom": "Custom"
                }[x],
                key="advanced_weight_mode"
            )
        
        if weight_mode == "custom":
            weights_input = st.text_input(
                "Custom Weights (%)",
                value="20, 20, 20, 20, 20",
                placeholder="Ex: 30, 25, 20, 15, 10",
                key="advanced_custom_weights"
            )
        else:
            weights_input = ""
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    assets = [a.strip().upper() for a in assets_input.split(",") if a.strip()]
    
    if not assets:
        st.warning("Please enter at least one ticker")
        return
    
    df = fetch_multiple_assets_pm(assets, period)
    
    if df.empty:
        st.error("Unable to fetch data. Check tickers.")
        return
    
    if weight_mode == "equal":
        weights = pm_core.create_equal_weights(df.columns.tolist())
    else:
        try:
            weight_values = [float(w.strip()) for w in weights_input.split(",")]
            if len(weight_values) != len(df.columns):
                weight_values = [100 / len(df.columns)] * len(df.columns)
        except:
            weight_values = [100 / len(df.columns)] * len(df.columns)
        
        total = sum(weight_values)
        weights = {asset: w/total for asset, w in zip(df.columns, weight_values)}
    
    st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
    st.markdown("""
    <h4 style="color: """ + COLORS["text"] + """; font-size: 18px; font-weight: 700; margin-bottom: 8px;">
        ADVANCED ANALYTICS
    </h4>
    <p style="color: """ + COLORS["text_secondary"] + """; font-size: 12px; margin-bottom: 20px;">
        Multi-scale analysis based on ESILV Market Risk course
    </p>
    """, unsafe_allow_html=True)
    
    returns = pm_core.calculate_returns(df)
    
    portfolio_returns = pd.Series(0.0, index=returns.index)
    for asset, weight in weights.items():
        if asset in returns.columns:
            portfolio_returns += returns[asset] * weight
    
    H_portfolio = estimate_hurst_exponent(portfolio_returns)
    
    hurst_data = []
    for asset in df.columns:
        H = estimate_hurst_exponent(returns[asset])
        hurst_data.append({"asset": asset, "hurst": H})
    
    hurst_df = pd.DataFrame(hurst_data)
    
    fig_hurst = go.Figure()
    
    colors = []
    for h in hurst_df["hurst"]:
        if h > 0.55:
            colors.append(COLORS["positive"])
        elif h < 0.45:
            colors.append(COLORS["negative"])
        else:
            colors.append(COLORS["warning"])
    
    fig_hurst.add_trace(go.Bar(
        x=hurst_df["asset"],
        y=hurst_df["hurst"],
        marker_color=colors,
        text=["{0:.3f}".format(h) for h in hurst_df["hurst"]],
        textposition="outside"
    ))
    
    fig_hurst.add_hline(y=0.5, line_dash="dash", line_color=COLORS["text_secondary"], 
                        annotation_text="Random Walk (H=0.5)")
    
    fig_hurst.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(family="'Inter', sans-serif", size=11, color=COLORS["text"]),
        margin=dict(l=50, r=30, t=30, b=50),
        yaxis=dict(title="Hurst Exponent", range=[0, 1])
    )
    
    msv = multi_scale_variance(portfolio_returns)
    fig_msv = go.Figure()
    
    if isinstance(msv, pd.DataFrame):
        if "annualized_vol" in msv.columns:
            y_data = msv["annualized_vol"]
            y_label = "Annualized Volatility (%)"
        elif "variance" in msv.columns:
            y_data = msv["variance"]
            y_label = "Variance"
        elif "volatility" in msv.columns:
            y_data = msv["volatility"]
            y_label = "Volatility"
        elif len(msv.columns) > 0:
            y_data = msv.iloc[:, 0]
            y_label = msv.columns[0]
        else:
            y_data = pd.Series([0])
            y_label = "Test Data"
            
        x_data = msv.index if "scale" not in msv.columns else msv["scale"]
    else:
        x_data = list(range(1, 11))
        y_data = pd.Series([0] * 10)
        y_label = "Multi-scale Analysis"
    
    fig_msv.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode="lines+markers",
        line=dict(color=COLORS["accent"], width=2),
        marker=dict(size=8)
    ))
    
    fig_msv.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(family="'Inter', sans-serif", size=11, color=COLORS["text"]),
        margin=dict(l=50, r=30, t=30, b=50),
        xaxis=dict(title="Time Scale (days)"),
        yaxis=dict(title=y_label)
    )
    
    port_prices = pm_core.portfolio_value(df, weights)
    fig_regimes = go.Figure()
    
    fig_regimes.add_trace(go.Scatter(
        x=port_prices.index,
        y=port_prices,
        mode="lines",
        name="Portfolio Value",
        line=dict(color=COLORS["accent"], width=2)
    ))
    
    ma_short = port_prices.rolling(window=20).mean()
    ma_long = port_prices.rolling(window=50).mean()
    
    bull_mask = ma_short > ma_long
    bear_mask = ma_short < ma_long
    volatility = port_prices.pct_change().rolling(window=20).std()
    high_vol_mask = volatility > volatility.quantile(0.75)
    
    if len(bull_mask) == len(port_prices) and bull_mask.sum() > 0:
        fig_regimes.add_trace(go.Scatter(
            x=port_prices.index[bull_mask],
            y=port_prices[bull_mask],
            mode="markers",
            name="Bull",
            marker=dict(color=COLORS["positive"], size=3)
        ))
    
    if len(bear_mask) == len(port_prices) and bear_mask.sum() > 0:
        fig_regimes.add_trace(go.Scatter(
            x=port_prices.index[bear_mask],
            y=port_prices[bear_mask],
            mode="markers",
            name="Bear",
            marker=dict(color=COLORS["negative"], size=3)
        ))
    
    if len(high_vol_mask) == len(port_prices) and high_vol_mask.sum() > 0:
        fig_regimes.add_trace(go.Scatter(
            x=port_prices.index[high_vol_mask],
            y=port_prices[high_vol_mask],
            mode="markers",
            name="High Vol",
            marker=dict(color=COLORS["warning"], size=3)
        ))
    
    fig_regimes.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(family="'Inter', sans-serif", size=11, color=COLORS["text"]),
        margin=dict(l=50, r=30, t=30, b=50),
        yaxis=dict(title="Portfolio Value"),
        legend=dict(orientation="h", y=1.1)
    )
    
    vr_test = variance_ratio_test(portfolio_returns)
    
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">MACHINE LEARNING ANALYSIS</div>', unsafe_allow_html=True)
    
    if st.button("Run Machine Learning Analysis", type="primary", use_container_width=True):
        with st.spinner("Training HMM and XGBoost models..."):
            try:
                ml_results = ml_advanced_analysis(df, weights, COLORS)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**HMM Market Regimes**")
                    st.plotly_chart(ml_results["hmm_fig"], use_container_width=True)
                    st.dataframe(ml_results["hmm_stats"], use_container_width=True)
                
                with col2:
                    st.markdown("**XGBoost Return Prediction**")
                    st.plotly_chart(ml_results["xgb_fig"], use_container_width=True)
                    st.metric("Prediction Accuracy (RMSE)", "{0:.6f}".format(ml_results["xgb_rmse"]))
                
                st.markdown("**Feature Importance**")
                st.plotly_chart(ml_results["importance_fig"], use_container_width=True)
                
                with st.expander("ML Analysis Interpretation"):
                    st.markdown("""
                    **HMM (Hidden Markov Model):**
                    - Detects different market regimes (bull, bear, sideways)
                    - Each regime has distinct return/volatility characteristics
                    - Colors show periods in each regime
                    
                    **XGBoost:**
                    - Predicts future portfolio returns
                    - RMSE measures prediction error (lower is better)
                    - Feature importance shows which factors drive predictions
                    """)
                    
            except Exception as e:
                st.error("ML Analysis Error: " + str(e))
                st.info("Make sure you have installed: pip install hmmlearn xgboost")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">HURST EXPONENT BY ASSET</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_hurst, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">INTERPRETATION</div>', unsafe_allow_html=True)
        
        behavior = "PERSISTENT" if H_portfolio > 0.55 else "RANDOM WALK" if 0.45 <= H_portfolio <= 0.55 else "ANTI-PERSISTENT"
        interpretation_text = """Portfolio Hurst Exponent: {0:.3f}

Interpretation:
- H > 0.55: Persistent (trending behavior, momentum)
- H = 0.50: Random walk (efficient market)
- H < 0.45: Anti-persistent (mean-reverting)

Your portfolio shows {1} behavior.""".format(H_portfolio, behavior)
        
        st.text_area("", interpretation_text, height=200, 
                    label_visibility="collapsed",
                    disabled=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">MULTI-SCALE VARIANCE</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_msv, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">VARIANCE RATIO TEST</div>', unsafe_allow_html=True)
        
        if not vr_test.empty:
            vr_display = vr_test.copy()
            vr_display.columns = ["Lag (days)", "Variance Ratio", "Z-statistic", "Interpretation"]
            st.dataframe(vr_display, use_container_width=True, hide_index=True)
        else:
            st.info("Insufficient data for variance ratio test")
        
        st.markdown("""
        <p style="color: #8b949e; font-size: 10px; margin-top: 12px;">
            Lo-MacKinlay test for random walk hypothesis
        </p>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">REGIME DETECTION</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_regimes, use_container_width=True)
    
    st.markdown("""
    <p style="color: #8b949e; font-size: 10px; margin-top: 12px;">
        Simple regime classification based on rolling statistics
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

main()