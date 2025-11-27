"""
Quant B - Dashboard Components
Custom weights, advanced metrics, visualizations
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import pandas as pd

COLORS = {
    "background": "#0d1117",
    "card": "#161b22",
    "border": "#30363d",
    "text": "#e6edf3",
    "green": "#3fb950",
    "red": "#f85149",
    "blue": "#58a6ff",
    "orange": "#d29922"
}

CARD_STYLE = {
    "backgroundColor": COLORS["card"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "8px",
    "padding": "20px",
    "marginBottom": "15px"
}


def create_weight_sliders(assets):
    """Create weight sliders for each asset."""
    sliders = []
    for asset in assets:
        sliders.append(
            html.Div([
                html.Label(f"{asset}", style={"color": COLORS["text"], "fontWeight": "bold"}),
                dcc.Slider(
                    id={"type": "weight-slider", "asset": asset},
                    min=0, max=100, step=5, value=100 // len(assets),
                    marks={0: "0%", 50: "50%", 100: "100%"},
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ], style={"marginBottom": "15px"})
        )
    return html.Div(sliders)


def create_portfolio_metrics_card(metrics):
    """Create portfolio metrics display."""
    ret_color = COLORS["green"] if metrics["annual_return"] >= 0 else COLORS["red"]
    
    return html.Div([
        html.Div([
            html.Span("Rendement annuel: ", style={"color": COLORS["text"]}),
            html.Span(f"{metrics['annual_return']}%", style={"color": ret_color, "fontWeight": "bold", "fontSize": "20px"})
        ], style={"marginBottom": "12px"}),
        
        html.Div([
            html.Span("Volatilite: ", style={"color": COLORS["text"]}),
            html.Span(f"{metrics['volatility']}%", style={"color": COLORS["orange"], "fontWeight": "bold", "fontSize": "20px"})
        ], style={"marginBottom": "12px"}),
        
        html.Div([
            html.Span("Sharpe Ratio: ", style={"color": COLORS["text"]}),
            html.Span(f"{metrics['sharpe_ratio']}", style={"color": COLORS["blue"], "fontWeight": "bold", "fontSize": "20px"})
        ], style={"marginBottom": "12px"}),
        
        html.Div([
            html.Span("Sortino Ratio: ", style={"color": COLORS["text"]}),
            html.Span(f"{metrics.get('sortino_ratio', 'N/A')}", style={"color": COLORS["blue"], "fontWeight": "bold", "fontSize": "20px"})
        ], style={"marginBottom": "12px"}),
        
        html.Div([
            html.Span("Max Drawdown: ", style={"color": COLORS["text"]}),
            html.Span(f"{metrics['max_drawdown']}%", style={"color": COLORS["red"], "fontWeight": "bold", "fontSize": "20px"})
        ], style={"marginBottom": "12px"}),
        
        html.Div([
            html.Span("Value at Risk (95%): ", style={"color": COLORS["text"]}),
            html.Span(f"{metrics.get('var_95', 'N/A')}%", style={"color": COLORS["red"], "fontWeight": "bold", "fontSize": "20px"})
        ], style={"marginBottom": "12px"}),
        
        html.Div([
            html.Span("Ratio Diversification: ", style={"color": COLORS["text"]}),
            html.Span(f"{metrics.get('diversification_ratio', 'N/A')}", style={"color": COLORS["green"], "fontWeight": "bold", "fontSize": "20px"})
        ])
    ])


def create_main_chart(df_normalized, portfolio_value, colors):
    """Create main performance chart."""
    fig = go.Figure()
    
    color_list = [COLORS["blue"], COLORS["green"], COLORS["orange"], COLORS["red"], "#a371f7", "#3fb9a5"]
    
    for i, col in enumerate(df_normalized.columns):
        fig.add_trace(go.Scatter(
            x=df_normalized.index,
            y=df_normalized[col],
            name=col,
            line=dict(color=color_list[i % len(color_list)], width=1.5)
        ))
    
    fig.add_trace(go.Scatter(
        x=portfolio_value.index,
        y=portfolio_value,
        name="PORTFOLIO",
        line=dict(color="white", width=3, dash="dash")
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="x unified"
    )
    
    return fig


def create_correlation_heatmap(corr_matrix):
    """Create correlation matrix heatmap."""
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale=[[0, COLORS["red"]], [0.5, "#1a1a1a"], [1, COLORS["green"]]],
        zmin=-1, zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size": 12}
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig


def create_weights_pie_chart(weights):
    """Create pie chart showing portfolio allocation."""
    fig = go.Figure(data=[go.Pie(
        labels=list(weights.keys()),
        values=list(weights.values()),
        hole=0.4,
        marker_colors=[COLORS["blue"], COLORS["green"], COLORS["orange"], COLORS["red"], "#a371f7"]
    )])
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1)
    )
    
    return fig
