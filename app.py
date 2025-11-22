"""
Single Asset Dashboard - Société Générale (Quant A)
"""
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

from single_asset.data_fetcher import fetch_data, get_current_price
from single_asset.strategies import (
    buy_and_hold, end_of_month, volatility_breakout,
    trend_following, golden_cross, rsi_oversold, macd_crossover
)
from single_asset.metrics import get_all_metrics

# === STYLES ===
COLORS = {
    "background": "#0a0a0a",
    "card": "#1a1a1a",
    "text": "#ffffff",
    "blue": "#00d4ff",
    "green": "#00ff88",
    "red": "#ff4444",
    "orange": "#ffa500",
    "border": "#333333"
}

CARD_STYLE = {
    "backgroundColor": COLORS["card"],
    "padding": "20px",
    "borderRadius": "10px",
    "marginBottom": "15px",
    "border": f"1px solid {COLORS['border']}"
}

#  APP 
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Single Asset Dashboard - SG"

STRATEGIES = {
    "buy_and_hold": buy_and_hold,
    "volatility_breakout": volatility_breakout,
    "trend_following": trend_following,
    "golden_cross": golden_cross,
    "rsi_oversold": rsi_oversold,
    "end_of_month": end_of_month,
    "macd_crossover": macd_crossover
}

#  LAYOUT 
app.layout = dbc.Container([
    dcc.Interval(id="refresh-interval", interval=5*60*1000, n_intervals=0),
    
    # Header
    html.Div([
        html.H1("SINGLE ASSET DASHBOARD", style={"color": COLORS["blue"], "fontWeight": "bold"}),
        html.P("Société Générale (GLE.PA)", style={"color": COLORS["text"], "opacity": "0.7"}),
        html.P(id="last-update", style={"color": COLORS["text"], "opacity": "0.5"})
    ], style={"textAlign": "center", "padding": "20px 0"}),
    
    # Contrôles
    dbc.Row([
        dbc.Col([
            html.Div(id="price-card", style=CARD_STYLE)
        ], md=3),
        dbc.Col([
            html.Div([
                html.Label("Période", style={"color": COLORS["text"]}),
                dbc.Select(
                    id="period-dropdown",
                    options=[
                        {"label": "1 Mois", "value": "1mo"},
                        {"label": "3 Mois", "value": "3mo"},
                        {"label": "6 Mois", "value": "6mo"},
                        {"label": "1 An", "value": "1y"},
                        {"label": "2 Ans", "value": "2y"}
                    ],
                    value="1y",
                    style={"backgroundColor": "#1a1a1a", "color": "#ffffff", "border": "1px solid #333333"}
                )
            ], style=CARD_STYLE)
        ], md=2),
        dbc.Col([
            html.Div([
                html.Label("Stratégie", style={"color": COLORS["text"]}),
                dbc.Select(
                    id="strategy-dropdown",
                    options=[
                        {"label": "Buy and Hold", "value": "buy_and_hold"},
                        {"label": "Volatility Breakout", "value": "volatility_breakout"},
                        {"label": "Trend Following", "value": "trend_following"},
                        {"label": "Golden Cross", "value": "golden_cross"},
                        {"label": "RSI Oversold", "value": "rsi_oversold"},
                        {"label": "End of Month", "value": "end_of_month"},
                        {"label": "📊 MACD Crossover", "value": "macd_crossover"}
                    ],
                    value="buy_and_hold",
                    style={"backgroundColor": "#1a1a1a", "color": "#ffffff", "border": "1px solid #333333"}
                )
            ], style=CARD_STYLE)
        ], md=3),
        dbc.Col([
            html.Div([
                html.Label("Capital Initial (€)", style={"color": COLORS["text"]}),
                dbc.Input(id="capital-input", type="number", value=10000,
                    style={"backgroundColor": COLORS["card"], "color": COLORS["text"], "border": f"1px solid {COLORS['border']}"})
            ], style=CARD_STYLE)
        ], md=2),
    ]),
    
    # Graphique principal
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Prix SG + Stratégie", style={"color": COLORS["text"]}),
                dcc.Graph(id="main-chart", style={"height": "500px"})
            ], style=CARD_STYLE)
        ], md=8),
        dbc.Col([
            html.Div([
                html.H5("Métriques", style={"color": COLORS["text"]}),
                html.Div(id="metrics-display")
            ], style=CARD_STYLE)
        ], md=4)
    ]),
    
    # Footer
    html.P("Auto-refresh: 5 min | Quant A Module",
           style={"textAlign": "center", "color": COLORS["text"], "opacity": "0.5", "marginTop": "20px"})

], fluid=True, style={"backgroundColor": COLORS["background"], "minHeight": "100vh", "padding": "20px"})


# CALLBACKS 

@callback(Output("last-update", "children"), Input("refresh-interval", "n_intervals"))
def update_timestamp(n):
    return f"Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"


@callback(Output("price-card", "children"), Input("refresh-interval", "n_intervals"))
def update_price(n):
    try:
        info = get_current_price()
        is_positive = info["change"] >= 0
        color = COLORS["green"] if is_positive else COLORS["red"]
        arrow = "▲" if is_positive else "▼"
        return [
            html.H6("Prix Actuel", style={"color": COLORS["text"], "opacity": "0.7"}),
            html.H2(f"{info['price']:.2f} €", style={"color": COLORS["text"]}),
            html.Span(f"{arrow} {info['change']:+.2f}%", style={"color": color, "fontWeight": "bold", "fontSize": "18px"})
        ]
    except:
        return html.P("Chargement...", style={"color": COLORS["text"]})


@callback(
    Output("main-chart", "figure"),
    Output("metrics-display", "children"),
    Input("period-dropdown", "value"),
    Input("strategy-dropdown", "value"),
    Input("capital-input", "value"),
    Input("refresh-interval", "n_intervals")
)
def update_charts(period, strategy, capital, n):
    capital = capital or 10000
    data = fetch_data(period)
    
    # Appliquer la stratégie
    result = STRATEGIES[strategy](data, initial_capital=capital)
    
    #  GRAPHIQUE : Prix + Stratégie 
    main_fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    main_fig.add_trace(
        go.Scatter(x=data.index, y=data['Close'], name="Prix SG (€)", 
                   line=dict(color=COLORS["blue"], width=2)),
        secondary_y=False
    )
    
    main_fig.add_trace(
        go.Scatter(x=result.index, y=result['portfolio_value'], name="Portefeuille (€)",
                   line=dict(color=COLORS["green"], width=2)),
        secondary_y=True
    )
    
    main_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    main_fig.update_yaxes(title_text="Prix SG (€)", secondary_y=False, color=COLORS["blue"])
    main_fig.update_yaxes(title_text="Portefeuille (€)", secondary_y=True, color=COLORS["green"])
    
    #  MÉTRIQUES 
    metrics = get_all_metrics(result)
    metrics_rows = []
    for name, value in metrics.items():
        if "Return" in name or "Drawdown" in name:
            color = COLORS["green"] if value >= 0 else COLORS["red"]
        elif "Sharpe" in name or "Calmar" in name:
            color = COLORS["green"] if value >= 1 else COLORS["orange"]
        else:
            color = COLORS["text"]
        
        metrics_rows.append(
            html.Div([
                html.Span(name, style={"color": COLORS["text"], "opacity": "0.7"}),
                html.Span(f"{value}", style={"color": color, "fontWeight": "bold", "float": "right"})
            ], style={"padding": "10px 0", "borderBottom": f"1px solid {COLORS['border']}"})
        )
    
    return main_fig, html.Div(metrics_rows)


if __name__ == "__main__":
    app.run(debug=True, port=8050)