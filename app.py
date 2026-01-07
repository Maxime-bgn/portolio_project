"""
Portfolio Dashboard - Streamlit Version
Pages: Portfolio | Advanced Analytics
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Import de vos modules existants
from utils.data_fetcher import fetch_multiple_assets, get_current_prices
from portfolio_module.portfolio_core import (
    create_equal_weights, normalize_weights, portfolio_value,
    correlation_matrix, analyze_portfolio, DEFAULT_ASSETS, calculate_returns
)
from portfolio_module.components import (
    COLORS, CARD_STYLE, create_portfolio_metrics_card,
    create_main_chart, create_correlation_heatmap, 
    create_weights_pie_chart, create_drawdown_chart
)
from portfolio_module.advanced_analytics import (
    estimate_hurst_exponent, multi_scale_variance,
    detect_regimes_simple, variance_ratio_test
)

# Configuration de la page
st.set_page_config(
    page_title="Portfolio Analytics | Quant B",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuration CSS personnalisée
st.markdown(f"""
<style>
    .stApp {{
        background-color: {COLORS["background"]};
    }}
    
    .main-header {{
        border-bottom: 1px solid {COLORS["border"]};
        padding: 24px 0;
        margin-bottom: 24px;
    }}
    
    .portfolio-card {{
        background-color: {COLORS["card"]};
        border-radius: 8px;
        padding: 20px;
        border: 1px solid {COLORS["border"]};
        margin-bottom: 20px;
    }}
    
    .price-card {{
        background-color: {COLORS["card"]};
        border-radius: 6px;
        padding: 15px;
        border: 1px solid {COLORS["border"]};
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    
    .stSelectbox, .stTextInput > div > div > input {{
        background-color: {COLORS["card"]} !important;
        color: {COLORS["text"]} !important;
        border-color: {COLORS["border"]} !important;
    }}
    
    .stSelectbox > div > div {{
        background-color: {COLORS["card"]} !important;
        color: {COLORS["text"]} !important;
    }}
    
    .section-title {{
        color: {COLORS["text"]};
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 16px;
    }}
    
    .footer {{
        text-align: center;
        color: {COLORS["text_secondary"]};
        font-size: 11px;
        opacity: 0.7;
        margin-top: 32px;
        padding-top: 24px;
        border-top: 1px solid {COLORS["border"]};
    }}
</style>
""", unsafe_allow_html=True)

# Fonction pour afficher les métriques principales dans Streamlit
def render_metrics_card_streamlit(metrics):
    """Affiche les métriques principales du portfolio dans Streamlit"""
    col1, col2, col3, col4 = st.columns(4)
    
    # Retour annualisé
    with col1:
        ret_color = COLORS["positive"] if metrics.get("annual_return", 0) >= 0 else COLORS["negative"]
        st.markdown(f"""
        <div style="background-color: {COLORS['card']}; border-radius: 6px; padding: 15px; border: 1px solid {COLORS['border']}; height: 100%;">
            <div style="font-size: 11px; color: {COLORS['text_secondary']}; margin-bottom: 5px;">RETURN</div>
            <div style="font-size: 22px; font-weight: 600; color: {ret_color}">
                {metrics.get('annual_return', metrics.get('return', 'N/A'))}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Volatilité
    with col2:
        st.markdown(f"""
        <div style="background-color: {COLORS['card']}; border-radius: 6px; padding: 15px; border: 1px solid {COLORS['border']}; height: 100%;">
            <div style="font-size: 11px; color: {COLORS['text_secondary']}; margin-bottom: 5px;">VOLATILITY</div>
            <div style="font-size: 22px; font-weight: 600; color: {COLORS['warning']}">
                {metrics.get('volatility', 'N/A')}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Sharpe Ratio
    with col3:
        st.markdown(f"""
        <div style="background-color: {COLORS['card']}; border-radius: 6px; padding: 15px; border: 1px solid {COLORS['border']}; height: 100%;">
            <div style="font-size: 11px; color: {COLORS['text_secondary']}; margin-bottom: 5px;">SHARPE RATIO</div>
            <div style="font-size: 22px; font-weight: 600; color: {COLORS['accent']}">
                {metrics.get('sharpe_ratio', metrics.get('sharpe', 'N/A'))}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Max Drawdown
    with col4:
        st.markdown(f"""
        <div style="background-color: {COLORS['card']}; border-radius: 6px; padding: 15px; border: 1px solid {COLORS['border']}; height: 100%;">
            <div style="font-size: 11px; color: {COLORS['text_secondary']}; margin-bottom: 5px;">MAX DRAWDOWN</div>
            <div style="font-size: 22px; font-weight: 600; color: {COLORS['negative']}">
                {metrics.get('max_drawdown', 'N/A')}%
            </div>
        </div>
        """, unsafe_allow_html=True)

# Initialisation de l'état de session
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'portfolio'

# Interface principale
def main():
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1 style="color: {COLORS['text']}; font-weight: 700; font-size: 28px; margin-bottom: 4px; letter-spacing: -0.5px;">
            PORTFOLIO ANALYTICS
        </h1>
        <p style="color: {COLORS['text_secondary']}; font-size: 14px; margin-bottom: 8px;">
            Multi-Asset Portfolio Management & Risk Analysis
        </p>
        <p style="color: {COLORS['positive']}; font-size: 11px; font-weight: 500;">
            Mis a jour: {datetime.now().strftime('%H:%M:%S')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("PORTFOLIO", use_container_width=True):
            st.session_state.current_page = 'portfolio'
            st.rerun()
    with col2:
        if st.button("ADVANCED ANALYTICS", use_container_width=True):
            st.session_state.current_page = 'advanced'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Contrôles de configuration
    with st.container():
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            assets_input = st.text_input(
                "Assets (tickers)",
                value=", ".join(DEFAULT_ASSETS),
                help="Séparer par des virgules: AAPL, GOOGL, MSFT"
            )
        
        with col2:
            period = st.selectbox(
                "Periode",
                options=["1mo", "3mo", "6mo", "1y", "2y"],
                index=3,
                format_func=lambda x: {
                    "1mo": "1 Mois",
                    "3mo": "3 Mois", 
                    "6mo": "6 Mois",
                    "1y": "1 An",
                    "2y": "2 Ans"
                }[x]
            )
        
        with col3:
            weight_mode = st.selectbox(
                "Mode Poids",
                options=["equal", "custom"],
                index=0,
                format_func=lambda x: {
                    "equal": "Egaux",
                    "custom": "Custom"
                }[x]
            )
        
        with col4:
            rebalancing = st.selectbox(
                "Rebalancing",
                options=["never", "monthly", "quarterly"],
                index=0,
                format_func=lambda x: {
                    "never": "Jamais",
                    "monthly": "Mensuel",
                    "quarterly": "Trimestriel"
                }[x]
            )
        
        with col5:
            benchmark = st.text_input(
                "Benchmark",
                value="SPY",
                placeholder="Ex: SPY"
            )
        
        if weight_mode == "custom":
            weights_input = st.text_input(
                "Poids Custom (%)",
                value="20, 20, 20, 20, 20",
                placeholder="Ex: 30, 25, 20, 15, 10"
            )
        else:
            weights_input = ""
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Parse les inputs
    assets = [a.strip().upper() for a in assets_input.split(",") if a.strip()]
    
    if not assets:
        st.warning("Veuillez entrer au moins un ticker")
        return
    
    # Récupération des données
    df = fetch_multiple_assets(assets, period)
    
    if df.empty:
        st.error("Impossible de récupérer les données. Vérifiez les tickers.")
        return
    
    # Calcul des poids
    if weight_mode == "equal":
        weights = create_equal_weights(df.columns.tolist())
    else:
        try:
            weight_values = [float(w.strip()) for w in weights_input.split(",")]
            if len(weight_values) != len(df.columns):
                weight_values = [100 / len(df.columns)] * len(df.columns)
        except:
            weight_values = [100 / len(df.columns)] * len(df.columns)
        
        total = sum(weight_values)
        weights = {asset: w/total for asset, w in zip(df.columns, weight_values)}
    
    # Benchmark
    market_returns = None
    if benchmark and benchmark.strip():
        try:
            benchmark_df = fetch_multiple_assets([benchmark.strip().upper()], period)
            if not benchmark_df.empty:
                market_returns = calculate_returns(benchmark_df).iloc[:, 0]
        except:
            pass
    
    # Affichage selon la page
    if st.session_state.current_page == 'portfolio':
        render_portfolio_page(df, assets, weights, rebalancing, market_returns)
    else:
        render_advanced_page(df, weights)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>
            <span style="margin-right: 20px;">Auto-refresh: 5 minutes</span>
            <span style="margin-right: 20px; opacity: 0.3;">•</span>
            <span style="margin-right: 20px;">Quant B Module</span>
            <span style="margin-right: 20px; opacity: 0.3;">•</span>
            <span>Professional Portfolio Analytics</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_portfolio_page(df, assets, weights, rebalancing, market_returns):
    """Affiche la page portfolio"""
    
    # Cartes de prix actuels
    prices = get_current_prices(assets)
    
    cols = st.columns(len(prices))
    for idx, (ticker, info) in enumerate(prices.items()):
        with cols[idx]:
            is_positive = info["change"] >= 0
            change_color = COLORS["positive"] if is_positive else COLORS["negative"]
            arrow = "▲" if is_positive else "▼"
            
            st.markdown(f"""
            <div class="price-card">
                <div style="margin-bottom: 8px;">
                    <span style="color: {COLORS['accent']}; font-weight: 700; font-size: 11px; letter-spacing: 0.5px;">
                        {ticker}
                    </span>
                </div>
                <div style="margin-bottom: 6px;">
                    <span style="color: {COLORS['text']}; font-size: 22px; font-weight: 600;">
                        ${info['price']:.2f}
                    </span>
                </div>
                <div>
                    <span style="color: {change_color}; font-size: 10px; margin-right: 2px;">
                        {arrow}
                    </span>
                    <span style="color: {change_color}; font-weight: 600; font-size: 13px;">
                        {abs(info['change']):.2f}%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Calculs
    port_value_series = portfolio_value(df, weights, rebalancing_freq=rebalancing)
    analysis = analyze_portfolio(df, weights, market_returns=market_returns)
    analysis["portfolio_value"] = port_value_series
    
    # Graphique principal et allocation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">PERFORMANCE (BASE 100)</div>', unsafe_allow_html=True)
        
        # Normalisation des prix
        df_norm = (df / df.iloc[0]) * 100
        main_fig = create_main_chart(df_norm, analysis["portfolio_value"], COLORS)
        st.plotly_chart(main_fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">ALLOCATION</div>', unsafe_allow_html=True)
        
        alloc_fig = create_weights_pie_chart(weights)
        st.plotly_chart(alloc_fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Drawdown et corrélation
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">DRAWDOWN ANALYSIS</div>', unsafe_allow_html=True)
        
        drawdown_fig = create_drawdown_chart(analysis["portfolio_value"])
        st.plotly_chart(drawdown_fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">CORRELATION MATRIX</div>', unsafe_allow_html=True)
        
        corr_fig = create_correlation_heatmap(analysis["correlation"])
        st.plotly_chart(corr_fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Métriques du portfolio (version simplifiée)
    st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">PORTFOLIO METRICS</div>', unsafe_allow_html=True)
    
    render_metrics_card_streamlit(analysis["portfolio"])
    
    # Métriques détaillées dans un expander
    with st.expander("Voir les métriques détaillées"):
        create_portfolio_metrics_card(analysis["portfolio"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tableau des actifs
    st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ASSET BREAKDOWN</div>', unsafe_allow_html=True)
    
    # Préparation des données pour le tableau
    asset_data = []
    for asset, metrics in analysis["assets"].items():
        asset_data.append({
            'Asset': asset,
            'Return (%)': f"{metrics['return']:.2f}",
            'Volatility (%)': f"{metrics['volatility']:.2f}",
            'Sharpe Ratio': f"{metrics['sharpe']:.2f}",
            'Weight (%)': f"{metrics['weight']:.2f}"
        })
    
    df_assets = pd.DataFrame(asset_data)
    
    # Afficher le tableau
    st.dataframe(df_assets, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_advanced_page(df, weights):
    """Affiche la page d'analyse avancée"""
    
    st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <h4 style="color: {COLORS['text']}; font-size: 18px; font-weight: 700; margin-bottom: 8px;">
        ADVANCED ANALYTICS
    </h4>
    <p style="color: {COLORS['text_secondary']}; font-size: 12px; margin-bottom: 20px;">
        Multi-scale analysis based on ESILV Market Risk course
    </p>
    """, unsafe_allow_html=True)
    
    # Calculs
    returns = calculate_returns(df)
    
    # Portfolio returns
    portfolio_returns = pd.Series(0.0, index=returns.index)
    for asset, weight in weights.items():
        if asset in returns.columns:
            portfolio_returns += returns[asset] * weight
    
    # Hurst exponent for portfolio
    H_portfolio = estimate_hurst_exponent(portfolio_returns)
    
    # Hurst per asset
    hurst_data = []
    for asset in df.columns:
        H = estimate_hurst_exponent(returns[asset])
        hurst_data.append({'asset': asset, 'hurst': H})
    
    hurst_df = pd.DataFrame(hurst_data)
    
    # Create Hurst chart
    fig_hurst = go.Figure()
    
    colors = []
    for h in hurst_df['hurst']:
        if h > 0.55:
            colors.append(COLORS["positive"])
        elif h < 0.45:
            colors.append(COLORS["negative"])
        else:
            colors.append(COLORS["warning"])
    
    fig_hurst.add_trace(go.Bar(
        x=hurst_df['asset'],
        y=hurst_df['hurst'],
        marker_color=colors,
        text=[f"{h:.3f}" for h in hurst_df['hurst']],
        textposition='outside'
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
    
    # Multi-scale variance
    msv = multi_scale_variance(portfolio_returns)

    fig_msv = go.Figure()

    # Utilisez 'var_ratio' au lieu de 'annualized_vol'
    if not msv.empty and 'var_ratio' in msv.columns:
        fig_msv.add_trace(go.Scatter(
            x=msv['scale'],
            y=msv['var_ratio'],  # <-- CHANGER ICI
            mode='lines+markers',
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
            yaxis=dict(title="Variance Ratio (vs daily)")  # <-- CHANGER ICI
        )
    else:
        st.warning("Données insuffisantes pour l'analyse multi-échelle")
    
    # Regime detection
    port_prices = portfolio_value(df, weights)
    regimes = detect_regimes_simple(port_prices)
    
    # Create regime chart
    fig_regimes = go.Figure()
    
    regime_colors = {
        'Bull': COLORS["positive"],
        'Bear': COLORS["negative"],
        'High Vol': COLORS["warning"],
        'Sideways': COLORS["info"],
        'Unknown': COLORS["text_secondary"]
    }
    
    # S'assurer que les index correspondent
    valid_data = regimes[regimes.index.isin(port_prices.index)]
    
    for regime_name in ['Bull', 'Bear', 'High Vol', 'Sideways']:
        regime_mask = valid_data == regime_name
        if regime_mask.sum() > 0:
            # Filtrer les données pour correspondre aux index
            regime_indices = valid_data.index[regime_mask]
            valid_prices = port_prices[port_prices.index.isin(regime_indices)]
            
            fig_regimes.add_trace(go.Scatter(
                x=valid_prices.index,
                y=valid_prices.values,
                mode='markers',
                name=regime_name,
                marker=dict(color=regime_colors[regime_name], size=4)
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
        
    # Variance ratio test
    vr_test = variance_ratio_test(portfolio_returns)
    
    # Hurst chart et interpretation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-title">HURST EXPONENT BY ASSET</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_hurst, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-title">INTERPRETATION</div>', unsafe_allow_html=True)
        
        interpretation_text = f"""Portfolio Hurst Exponent: {H_portfolio:.3f}

Interpretation:
- H > 0.55: Persistent (trending behavior, momentum)
- H = 0.50: Random walk (efficient market)
- H < 0.45: Anti-persistent (mean-reverting)

Your portfolio shows {"PERSISTENT" if H_portfolio > 0.55 else "RANDOM WALK" if 0.45 <= H_portfolio <= 0.55 else "ANTI-PERSISTENT"} behavior."""
        
        st.text_area("", interpretation_text, height=200, 
                    label_visibility="collapsed",
                    disabled=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Multi-scale variance et variance ratio
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">MULTI-SCALE VARIANCE</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_msv, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">VARIANCE RATIO TEST</div>', unsafe_allow_html=True)
        
        if not vr_test.empty:
            vr_display = vr_test.copy()
            vr_display.columns = ['Lag (days)', 'Variance Ratio', 'Z-statistic', 'Interpretation']
            st.dataframe(vr_display, use_container_width=True, hide_index=True)
        else:
            st.info("Données insuffisantes pour le test de variance ratio")
        
        st.markdown("""
        <p style="color: #8b949e; font-size: 10px; margin-top: 12px;">
            Lo-MacKinlay test for random walk hypothesis
        </p>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Régime detection
    st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">REGIME DETECTION</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_regimes, use_container_width=True)
    
    st.markdown("""
    <p style="color: #8b949e; font-size: 10px; margin-top: 12px;">
        Simple regime classification based on rolling statistics
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()