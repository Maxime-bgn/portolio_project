"""
Quant B - Portfolio Components
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit as st

COLORS = {
    "background": "#0a0e1a",
    "card": "#111828",
    "border": "#1f2937",
    "text": "#e5e7eb",
    "text_secondary": "#9ca3af",
    "accent": "#3b82f6",
    "positive": "#10b981",
    "negative": "#ef4444",
    "warning": "#f59e0b",
    "info": "#06b6d4"
}

CARD_STYLE = {
    "backgroundColor": COLORS["card"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "4px",
    "padding": "24px",
    "marginBottom": "16px"
}


def create_section_divider(title=""):
    st.markdown(f"""
    <div style="height: 1px; background-color: {COLORS['border']}; margin-top: 8px; margin-bottom: 16px;"></div>
    """, unsafe_allow_html=True)


def display_metric_line(label, value, color=None, sublabel=None):
    if color is None:
        color = COLORS["text"]
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"""
        <div style="color: {COLORS['text_secondary']}; font-size: 11px; font-weight: 500; 
                    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
            {label}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: right;">
            <span style="color: {color}; font-size: 20px; font-weight: 600; line-height: 1.2;">
                {value}
            </span>
            {f'<span style="color: {COLORS["text_secondary"]}; font-size: 12px; margin-left: 4px;">{sublabel}</span>' if sublabel else ''}
        </div>
        """, unsafe_allow_html=True)


def create_portfolio_metrics_card(metrics):
    # Section Returns & Risk
    st.markdown(f"""
    <div style="color: {COLORS['text']}; font-size: 10px; font-weight: 700; 
                letter-spacing: 1px; margin-bottom: 16px; text-transform: uppercase;">
        RETURNS & RISK
    </div>
    """, unsafe_allow_html=True)
    
    ret_color = COLORS["positive"] if metrics.get("annual_return", 0) >= 0 else COLORS["negative"]
    
    display_metric_line("Annual Return", f"{metrics.get('annual_return', 'N/A')}%", ret_color)
    display_metric_line("Volatility", f"{metrics.get('volatility', 'N/A')}%", COLORS["text"])
    display_metric_line("Downside Deviation", f"{metrics.get('downside_deviation', 'N/A')}%", COLORS["text_secondary"])
    
    create_section_divider()
    st.markdown(f"""
    <div style="color: {COLORS['text']}; font-size: 10px; font-weight: 700; 
                letter-spacing: 1px; margin-bottom: 16px; text-transform: uppercase;">
        RISK-ADJUSTED PERFORMANCE
    </div>
    """, unsafe_allow_html=True)
    
    display_metric_line("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 'N/A')}", COLORS["accent"])
    display_metric_line("Sortino Ratio", f"{metrics.get('sortino_ratio', 'N/A')}", COLORS["info"])
    display_metric_line("Calmar Ratio", f"{metrics.get('calmar_ratio', 'N/A')}", COLORS["text"])
    
    create_section_divider()
    st.markdown(f"""
    <div style="color: {COLORS['text']}; font-size: 10px; font-weight: 700; 
                letter-spacing: 1px; margin-bottom: 16px; text-transform: uppercase;">
        DRAWDOWN ANALYSIS
    </div>
    """, unsafe_allow_html=True)
    
    display_metric_line("Maximum Drawdown", f"{metrics.get('max_drawdown', 'N/A')}%", COLORS["negative"])
    display_metric_line("Current Drawdown", f"{metrics.get('current_drawdown', 'N/A')}%", COLORS["warning"])
    display_metric_line("Ulcer Index", f"{metrics.get('ulcer_index', 'N/A')}", COLORS["text_secondary"])
    
    create_section_divider()
    st.markdown(f"""
    <div style="color: {COLORS['text']}; font-size: 10px; font-weight: 700; 
                letter-spacing: 1px; margin-bottom: 16px; text-transform: uppercase;">
        VALUE AT RISK
    </div>
    """, unsafe_allow_html=True)
    
    display_metric_line("VaR (95%)", f"{metrics.get('var_95', 'N/A')}%", COLORS["warning"])
    display_metric_line("CVaR (95%)", f"{metrics.get('cvar_95', 'N/A')}%", COLORS["negative"])
    
    create_section_divider()
    st.markdown(f"""
    <div style="color: {COLORS['text']}; font-size: 10px; font-weight: 700; 
                letter-spacing: 1px; margin-bottom: 16px; text-transform: uppercase;">
        DIVERSIFICATION
    </div>
    """, unsafe_allow_html=True)
    
    display_metric_line("Diversification Ratio", f"{metrics.get('diversification_ratio', 'N/A')}", COLORS["positive"])
    display_metric_line("Win Rate", f"{metrics.get('win_rate', 'N/A')}%", COLORS["info"])
    if 'beta' in metrics:
        create_section_divider()
        
        st.markdown(f"""
        <div style="color: {COLORS['text']}; font-size: 10px; font-weight: 700; 
                    letter-spacing: 1px; margin-bottom: 16px; text-transform: uppercase;">
            MARKET EXPOSURE
        </div>
        """, unsafe_allow_html=True)
        
        display_metric_line("Beta", f"{metrics.get('beta', 'N/A')}", COLORS["accent"])
        
        alpha_color = COLORS["positive"] if metrics.get('alpha', 0) > 0 else COLORS["negative"]
        display_metric_line("Alpha", f"{metrics.get('alpha', 'N/A')}%", alpha_color)


def create_main_chart(df_normalized, portfolio_value, colors):
    fig = go.Figure()
    
    color_palette = [
        "#3b82f6",  # Blue
        "#10b981",  # Green
        "#f59e0b",  # Amber
        "#ef4444",  # Red
        "#8b5cf6",  # Purple
        "#06b6d4"   # Cyan
    ]
    for i, col in enumerate(df_normalized.columns):
        fig.add_trace(go.Scatter(
            x=df_normalized.index,
            y=df_normalized[col],
            name=col,
            line=dict(
                color=color_palette[i % len(color_palette)],
                width=1.5
            ),
            opacity=0.6
        ))
    fig.add_trace(go.Scatter(
        x=portfolio_value.index,
        y=portfolio_value,
        name="PORTFOLIO",
        line=dict(
            color="#ffffff",
            width=2.5
        ),
        opacity=1.0
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(
            family="'Inter', -apple-system, system-ui, sans-serif",
            size=11,
            color=COLORS["text"]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10)
        ),
        margin=dict(l=50, r=30, t=30, b=50),
        hovermode="x unified",
        xaxis=dict(
            gridcolor=COLORS["border"],
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor=COLORS["border"],
            showgrid=True,
            zeroline=False,
            title=dict(
                text="Indexed Value",
                font=dict(size=10)
            )
        )
    )
    
    return fig


def create_correlation_heatmap(corr_matrix):
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale=[
            [0, "#ef4444"],
            [0.5, "#1f2937"],
            [1, "#10b981"]
        ],
        zmin=-1, zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size": 10, "color": COLORS["text"]},
        colorbar=dict(
            title="",
            titleside="right",
            tickfont=dict(size=9)
        )
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(
            family="'Inter', -apple-system, system-ui, sans-serif",
            size=10,
            color=COLORS["text"]
        ),
        margin=dict(l=70, r=30, t=30, b=70),
        xaxis=dict(side="bottom", tickfont=dict(size=10)),
        yaxis=dict(side="left", tickfont=dict(size=10))
    )
    
    return fig


def create_weights_pie_chart(weights):
    colors_list = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"]
    
    fig = go.Figure(data=[go.Pie(
        labels=list(weights.keys()),
        values=list(weights.values()),
        hole=0.5,
        marker_colors=colors_list[:len(weights)],
        textinfo='label+percent',
        textfont=dict(size=11, color=COLORS["text"]),
        textposition='outside'
    )])
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(
            family="'Inter', -apple-system, system-ui, sans-serif",
            size=10,
            color=COLORS["text"]
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False
    )
    
    return fig


def create_drawdown_chart(portfolio_value):
    running_max = portfolio_value.expanding().max()
    drawdown = (portfolio_value - running_max) / running_max * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=drawdown.index,
        y=drawdown,
        fill='tozeroy',
        name='Drawdown',
        line=dict(color=COLORS["negative"], width=0),
        fillcolor='rgba(239, 68, 68, 0.2)'
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(
            family="'Inter', -apple-system, system-ui, sans-serif",
            size=11,
            color=COLORS["text"]
        ),
        margin=dict(l=50, r=30, t=30, b=50),
        xaxis=dict(
            gridcolor=COLORS["border"],
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor=COLORS["border"],
            showgrid=True,
            zeroline=True,
            zerolinecolor=COLORS["border"],
            title=dict(
                text="Drawdown (%)",
                font=dict(size=10)
            ),
            tickformat=".1f"
        ),
        hovermode="x unified"
    )
    
    return fig