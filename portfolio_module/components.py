"""
Quant B - Dashboard Components
Professional institutional design
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Professional color scheme (institutional grade)
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


def create_section_divider(title):
    """Professional section divider."""
    return html.Div([
        html.Div(style={
            "height": "1px",
            "backgroundColor": COLORS["border"],
            "marginTop": "8px",
            "marginBottom": "16px"
        })
    ])


def create_metric_line(label, value, color=None, sublabel=None):
    """Single metric line - institutional style."""
    if color is None:
        color = COLORS["text"]
    
    return html.Div([
        html.Div([
            html.Span(label, style={
                "color": COLORS["text_secondary"],
                "fontSize": "11px",
                "fontWeight": "500",
                "textTransform": "uppercase",
                "letterSpacing": "0.5px"
            }),
        ]),
        html.Div([
            html.Span(str(value), style={
                "color": color,
                "fontSize": "20px",
                "fontWeight": "600",
                "lineHeight": "1.2"
            }),
            html.Span(f"  {sublabel}" if sublabel else "", style={
                "color": COLORS["text_secondary"],
                "fontSize": "12px",
                "marginLeft": "4px"
            })
        ])
    ], style={"marginBottom": "16px"})


def create_portfolio_metrics_card(metrics):
    """Institutional-grade metrics display."""
    
    ret_color = COLORS["positive"] if metrics["annual_return"] >= 0 else COLORS["negative"]
    
    return html.Div([
        # Returns & Risk
        html.Div([
            html.H6("RETURNS & RISK", style={
                "color": COLORS["text"],
                "fontSize": "10px",
                "fontWeight": "700",
                "letterSpacing": "1px",
                "marginBottom": "16px",
                "textTransform": "uppercase"
            }),
            create_metric_line("Annual Return", f"{metrics['annual_return']}%", ret_color),
            create_metric_line("Volatility", f"{metrics['volatility']}%", COLORS["text"]),
            create_metric_line("Downside Deviation", 
                             f"{metrics.get('downside_deviation', 'N/A')}%", 
                             COLORS["text_secondary"]),
        ]),
        
        create_section_divider(""),
        
        # Risk-Adjusted Returns
        html.Div([
            html.H6("RISK-ADJUSTED PERFORMANCE", style={
                "color": COLORS["text"],
                "fontSize": "10px",
                "fontWeight": "700",
                "letterSpacing": "1px",
                "marginBottom": "16px",
                "textTransform": "uppercase"
            }),
            create_metric_line("Sharpe Ratio", 
                             f"{metrics['sharpe_ratio']}", 
                             COLORS["accent"]),
            create_metric_line("Sortino Ratio", 
                             f"{metrics.get('sortino_ratio', 'N/A')}", 
                             COLORS["info"]),
            create_metric_line("Calmar Ratio", 
                             f"{metrics.get('calmar_ratio', 'N/A')}", 
                             COLORS["text"]),
        ]),
        
        create_section_divider(""),
        
        # Drawdown Analysis
        html.Div([
            html.H6("DRAWDOWN ANALYSIS", style={
                "color": COLORS["text"],
                "fontSize": "10px",
                "fontWeight": "700",
                "letterSpacing": "1px",
                "marginBottom": "16px",
                "textTransform": "uppercase"
            }),
            create_metric_line("Maximum Drawdown", 
                             f"{metrics['max_drawdown']}%", 
                             COLORS["negative"]),
            create_metric_line("Current Drawdown", 
                             f"{metrics.get('current_drawdown', 'N/A')}%", 
                             COLORS["warning"]),
            create_metric_line("Ulcer Index", 
                             f"{metrics.get('ulcer_index', 'N/A')}", 
                             COLORS["text_secondary"]),
        ]),
        
        create_section_divider(""),
        
        # Risk Metrics
        html.Div([
            html.H6("VALUE AT RISK", style={
                "color": COLORS["text"],
                "fontSize": "10px",
                "fontWeight": "700",
                "letterSpacing": "1px",
                "marginBottom": "16px",
                "textTransform": "uppercase"
            }),
            create_metric_line("VaR (95%)", 
                             f"{metrics.get('var_95', 'N/A')}%", 
                             COLORS["warning"]),
            create_metric_line("CVaR (95%)", 
                             f"{metrics.get('cvar_95', 'N/A')}%", 
                             COLORS["negative"]),
        ]),
        
        create_section_divider(""),
        
        # Diversification
        html.Div([
            html.H6("DIVERSIFICATION", style={
                "color": COLORS["text"],
                "fontSize": "10px",
                "fontWeight": "700",
                "letterSpacing": "1px",
                "marginBottom": "16px",
                "textTransform": "uppercase"
            }),
            create_metric_line("Diversification Ratio", 
                             f"{metrics.get('diversification_ratio', 'N/A')}", 
                             COLORS["positive"]),
            create_metric_line("Win Rate", 
                             f"{metrics.get('win_rate', 'N/A')}%", 
                             COLORS["info"]),
        ]),
        
        # Market Exposure (if available)
        html.Div([
            create_section_divider(""),
            html.H6("MARKET EXPOSURE", style={
                "color": COLORS["text"],
                "fontSize": "10px",
                "fontWeight": "700",
                "letterSpacing": "1px",
                "marginBottom": "16px",
                "textTransform": "uppercase"
            }),
            create_metric_line("Beta", 
                             f"{metrics.get('beta', 'N/A')}", 
                             COLORS["accent"]),
            create_metric_line("Alpha", 
                             f"{metrics.get('alpha', 'N/A')}%", 
                             COLORS["positive"] if metrics.get('alpha', 0) > 0 else COLORS["negative"]),
        ], style={"display": "block" if 'beta' in metrics else "none"})
        
    ], style={"maxHeight": "650px", "overflowY": "auto"})


def create_main_chart(df_normalized, portfolio_value, colors):
    """Professional performance chart."""
    fig = go.Figure()
    
    color_palette = [
        "#3b82f6",  # Blue
        "#10b981",  # Green
        "#f59e0b",  # Amber
        "#ef4444",  # Red
        "#8b5cf6",  # Purple
        "#06b6d4"   # Cyan
    ]
    
    # Individual assets
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
    
    # Portfolio (emphasized)
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
    """Professional correlation heatmap."""
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
    """Professional allocation chart."""
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
    """Professional underwater plot."""
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
