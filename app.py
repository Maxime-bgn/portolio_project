"""
Portfolio Dashboard - Main Application
Integrates Quant A (single asset) and Quant B (portfolio)
"""

from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

from utils import fetch_multiple_assets, get_current_prices
from portfolio_module.portfolio_core import (
    create_equal_weights, normalize_weights, portfolio_value,
    correlation_matrix, analyze_portfolio, DEFAULT_ASSETS
)
from quant_b.components import (
    COLORS, CARD_STYLE, create_portfolio_metrics_card,
    create_main_chart, create_correlation_heatmap, create_weights_pie_chart
)

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
app.title = "Portfolio Dashboard"
server = app.server

REFRESH_INTERVAL = 5 * 60 * 1000

# ============================================
# LAYOUT
# ============================================
app.layout = dbc.Container([
    dcc.Interval(id="refresh-interval", interval=REFRESH_INTERVAL, n_intervals=0),
    dcc.Store(id="prices-store"),
    
    # Header
    html.Div([
        html.H1("PORTFOLIO DASHBOARD", style={"color": COLORS["blue"], "fontWeight": "bold"}),
        html.P(id="last-update", style={"color": COLORS["text"], "opacity": "0.6"})
    ], style={"textAlign": "center", "padding": "20px 0"}),
    
    # Controls Row
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("Assets", style={"color": COLORS["text"]}),
                dbc.Input(id="assets-input", value=", ".join(DEFAULT_ASSETS),
                    style={"backgroundColor": COLORS["card"], "border": f"1px solid {COLORS['border']}", "color": COLORS["text"]})
            ], style=CARD_STYLE)
        ], md=4),
        dbc.Col([
            html.Div([
                html.Label("Periode", style={"color": COLORS["text"]}),
                dcc.Dropdown(id="period-dropdown",
                    options=[{"label": "1 Mois", "value": "1mo"}, {"label": "3 Mois", "value": "3mo"},
                             {"label": "6 Mois", "value": "6mo"}, {"label": "1 An", "value": "1y"}, {"label": "2 Ans", "value": "2y"}],
                    value="1y", clearable=False)
            ], style=CARD_STYLE)
        ], md=2),
        dbc.Col([
            html.Div([
                html.Label("Mode Poids", style={"color": COLORS["text"]}),
                dcc.Dropdown(id="weight-mode",
                    options=[{"label": "Egaux", "value": "equal"}, {"label": "Custom", "value": "custom"}],
                    value="equal", clearable=False)
            ], style=CARD_STYLE)
        ], md=2),
        dbc.Col([
            html.Div([
                html.Label("Rebalancing", style={"color": COLORS["text"]}),
                dcc.Dropdown(id="rebalancing-freq",
                    options=[{"label": "Jamais", "value": "never"}, {"label": "Mensuel", "value": "monthly"},
                             {"label": "Trimestriel", "value": "quarterly"}, {"label": "Annuel", "value": "yearly"}],
                    value="never", clearable=False)
            ], style=CARD_STYLE)
        ], md=2),
    ]),
    
    # Custom Weights Section
    html.Div(id="custom-weights-section"),
    
    # Price Cards
    html.Div(id="price-cards", style={"marginBottom": "20px"}),
    
    # Charts Row 1
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Performance (base 100)", style={"color": COLORS["text"]}),
                dcc.Graph(id="main-chart", style={"height": "400px"})
            ], style=CARD_STYLE)
        ], md=8),
        dbc.Col([
            html.Div([
                html.H5("Allocation", style={"color": COLORS["text"]}),
                dcc.Graph(id="allocation-chart", style={"height": "400px"})
            ], style=CARD_STYLE)
        ], md=4)
    ]),
    
    # Charts Row 2
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Correlation Matrix", style={"color": COLORS["text"]}),
                dcc.Graph(id="correlation-chart", style={"height": "350px"})
            ], style=CARD_STYLE)
        ], md=6),
        dbc.Col([
            html.Div([
                html.H5("Metriques Portfolio", style={"color": COLORS["text"]}),
                html.Div(id="portfolio-metrics")
            ], style=CARD_STYLE)
        ], md=3),
        dbc.Col([
            html.Div([
                html.H5("Metriques Assets", style={"color": COLORS["text"]}),
                html.Div(id="asset-metrics", style={"maxHeight": "300px", "overflowY": "auto"})
            ], style=CARD_STYLE)
        ], md=3)
    ]),
    
    # Footer
    html.P("Auto-refresh: 5 min | Quant B Module", 
           style={"textAlign": "center", "color": COLORS["text"], "opacity": "0.5", "marginTop": "20px"})
    
], fluid=True, style={"backgroundColor": COLORS["background"], "minHeight": "100vh", "padding": "20px"})


# ============================================
# CALLBACKS
# ============================================

@callback(Output("last-update", "children"), Input("refresh-interval", "n_intervals"))
def update_timestamp(n):
    return f"Derniere mise a jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"


@callback(Output("price-cards", "children"),
          Input("assets-input", "value"), Input("refresh-interval", "n_intervals"))
def update_price_cards(assets_str, n):
    if not assets_str:
        return html.P("Entrez des assets", style={"color": COLORS["text"]})
    assets = [a.strip().upper() for a in assets_str.split(",") if a.strip()]
    prices = get_current_prices(assets)
    cards = []
    for ticker, info in prices.items():
        is_positive = info["change"] >= 0
        change_color = COLORS["green"] if is_positive else COLORS["red"]
        arrow = "+" if is_positive else ""
        card = dbc.Col([
            html.Div([
                html.H6(ticker, style={"color": COLORS["text"], "opacity": "0.7", "fontSize": "12px"}),
                html.H4(f"{info['price']:.2f}", style={"color": COLORS["text"]}),
                html.Span(f"{arrow}{info['change']:.2f}%", style={"color": change_color, "fontWeight": "bold"})
            ], style=CARD_STYLE)
        ], md=2)
        cards.append(card)
    return dbc.Row(children=cards)


@callback(
    Output("main-chart", "figure"), Output("correlation-chart", "figure"),
    Output("allocation-chart", "figure"), Output("portfolio-metrics", "children"),
    Output("asset-metrics", "children"),
    Input("assets-input", "value"), Input("period-dropdown", "value"),
    Input("weights-input", "value"), Input("refresh-interval", "n_intervals"))
def update_all(assets_str, period, weights_str, n):
    empty = go.Figure()
    empty.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], plot_bgcolor=COLORS["card"])
    
    if not assets_str:
        return empty, empty, empty, "", ""
    
    assets = [a.strip().upper() for a in assets_str.split(",") if a.strip()]
    df = fetch_multiple_assets(assets, period)
    
    if df.empty:
        empty.add_annotation(text="Aucune donnee", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return empty, empty, empty, "Pas de donnees", "Pas de donnees"
    
    # Parse custom weights
    try:
        weight_values = [float(w.strip()) for w in weights_str.split(",")]
        if len(weight_values) != len(df.columns):
            weight_values = [100 / len(df.columns)] * len(df.columns)
    except:
        weight_values = [100 / len(df.columns)] * len(df.columns)
    
    # Normalize to sum to 1
    total = sum(weight_values)
    weights = {asset: w / total for asset, w in zip(df.columns, weight_values)}
    
    # Analysis
    analysis = analyze_portfolio(df, weights)
    
    # Main Chart
    df_norm = (df / df.iloc[0]) * 100
    main_fig = create_main_chart(df_norm, analysis["portfolio_value"], COLORS)
    
    # Correlation
    corr_fig = create_correlation_heatmap(analysis["correlation"])
    
    # Allocation Pie
    alloc_fig = create_weights_pie_chart(weights)
    
    # Portfolio Metrics
    portfolio_metrics = create_portfolio_metrics_card(analysis["portfolio"])
    
    # Asset Metrics
    am = analysis["assets"]
    asset_rows = []
    for asset, data in am.items():
        ret_col = COLORS["green"] if data["return"] >= 0 else COLORS["red"]
        asset_rows.append(html.Div([
            html.Span(f"{asset}", style={"color": COLORS["text"], "fontWeight": "bold", "marginRight": "10px"}),
            html.Span(f"R:{data['return']}%", style={"color": ret_col, "marginRight": "8px"}),
            html.Span(f"Vol:{data['volatility']}%", style={"color": COLORS["orange"], "marginRight": "8px"}),
            html.Span(f"Sharpe:{data['sharpe']}", style={"color": COLORS["blue"]})
        ], style={"marginBottom": "10px", "padding": "8px", "backgroundColor": COLORS["background"], "borderRadius": "4px"}))
    
    return main_fig, corr_fig, alloc_fig, portfolio_metrics, html.Div(asset_rows)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
