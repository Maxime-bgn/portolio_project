"""
Portfolio Dashboard - Main Application
Professional dark theme for financial data visualization
"""

from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from utils import fetch_multiple_assets, get_current_prices

# ============================================
# APP INITIALIZATION
# ============================================
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
app.title = "Portfolio Dashboard"
server = app.server  # For deployment

# ============================================
# CONSTANTS
# ============================================
DEFAULT_ASSETS = ["AAPL", "MSFT", "GOOGL"]
REFRESH_INTERVAL = 5 * 60 * 1000  # 5 minutes in ms

# ============================================
# CUSTOM STYLES
# ============================================
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

# ============================================
# LAYOUT
# ============================================
app.layout = dbc.Container([
    # Auto-refresh component
    dcc.Interval(
        id="refresh-interval",
        interval=REFRESH_INTERVAL,
        n_intervals=0
    ),
    
    # Store for assets
    dcc.Store(id="assets-store", data=DEFAULT_ASSETS),
    
    # Header
    html.Div([
        html.H1("📈 PORTFOLIO DASHBOARD", 
                style={"color": COLORS["blue"], "fontWeight": "bold", "marginBottom": "5px"}),
        html.P(id="last-update", 
               style={"color": COLORS["text"], "opacity": "0.6", "fontSize": "14px"})
    ], style={"textAlign": "center", "padding": "20px 0"}),
    
    # Controls Row
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("Assets (séparés par virgules)", 
                          style={"color": COLORS["text"], "marginBottom": "8px"}),
                dbc.Input(
                    id="assets-input",
                    value="AAPL, MSFT, GOOGL",
                    placeholder="Ex: AAPL, TSLA, BTC-USD",
                    style={"backgroundColor": COLORS["card"], "border": f"1px solid {COLORS['border']}", "color": COLORS["text"]}
                )
            ], style=CARD_STYLE)
        ], md=8),
        dbc.Col([
            html.Div([
                html.Label("Période", style={"color": COLORS["text"], "marginBottom": "8px"}),
                dcc.Dropdown(
                    id="period-dropdown",
                    options=[
                        {"label": "1 Mois", "value": "1mo"},
                        {"label": "3 Mois", "value": "3mo"},
                        {"label": "6 Mois", "value": "6mo"},
                        {"label": "1 An", "value": "1y"},
                        {"label": "2 Ans", "value": "2y"},
                    ],
                    value="1y",
                    clearable=False,
                    style={"backgroundColor": COLORS["card"]}
                )
            ], style=CARD_STYLE)
        ], md=4)
    ], className="mb-3"),
    
    # Price Cards Row
    html.Div(id="price-cards", style={"marginBottom": "20px"}),
    
    # Main Chart
    html.Div([
        dcc.Graph(id="main-chart", style={"height": "500px"})
    ], style=CARD_STYLE),
    
    # Footer
    html.Div([
        html.P("🔄 Données actualisées automatiquement toutes les 5 minutes",
               style={"textAlign": "center", "color": COLORS["text"], "opacity": "0.5", "marginTop": "20px"})
    ])
    
], fluid=True, style={"backgroundColor": COLORS["background"], "minHeight": "100vh", "padding": "20px"})


# ============================================
# CALLBACKS
# ============================================

@callback(
    Output("last-update", "children"),
    Input("refresh-interval", "n_intervals")
)
def update_timestamp(n):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return f"Dernière mise à jour : {now}"


@callback(
    Output("price-cards", "children"),
    Input("assets-input", "value"),
    Input("refresh-interval", "n_intervals")
)
def update_price_cards(assets_str, n):
    if not assets_str:
        return html.P("Entrez des assets", style={"color": COLORS["text"]})
    
    assets = [a.strip().upper() for a in assets_str.split(",") if a.strip()]
    prices = get_current_prices(assets)
    
    cards = []
    for ticker, info in prices.items():
        is_positive = info["change"] >= 0
        change_color = COLORS["green"] if is_positive else COLORS["red"]
        arrow = "▲" if is_positive else "▼"
        
        card = dbc.Col([
            html.Div([
                html.H6(info["name"], style={"color": COLORS["text"], "opacity": "0.7", "marginBottom": "5px", "fontSize": "12px"}),
                html.H3(f"{info['price']:.2f}", style={"color": COLORS["text"], "marginBottom": "5px"}),
                html.Span(f"{arrow} {abs(info['change']):.2f}%", style={"color": change_color, "fontWeight": "bold"})
            ], style=CARD_STYLE)
        ], md=12//len(assets) if len(assets) <= 4 else 3)
        
        cards.append(card)
    
    return dbc.Row(cards)


@callback(
    Output("main-chart", "figure"),
    Input("assets-input", "value"),
    Input("period-dropdown", "value"),
    Input("refresh-interval", "n_intervals")
)
def update_chart(assets_str, period, n):
    if not assets_str:
        return go.Figure()
    
    assets = [a.strip().upper() for a in assets_str.split(",") if a.strip()]
    df = fetch_multiple_assets(assets, period)
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Aucune donnée disponible", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], plot_bgcolor=COLORS["card"])
        return fig
    
    # Normalize to 100 for comparison
    df_normalized = (df / df.iloc[0]) * 100
    
    fig = go.Figure()
    
    colors = [COLORS["blue"], COLORS["green"], COLORS["orange"], COLORS["red"], "#a371f7", "#3fb9a5"]
    
    for i, col in enumerate(df_normalized.columns):
        fig.add_trace(go.Scatter(
            x=df_normalized.index,
            y=df_normalized[col],
            name=col,
            mode="lines",
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f"<b>{col}</b><br>%{{x|%d %b %Y}}<br>%{{y:.2f}}<extra></extra>"
        ))
    
    fig.update_layout(
        title=dict(text="Performance comparée (base 100)", font=dict(color=COLORS["text"])),
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        xaxis=dict(
            gridcolor=COLORS["border"],
            showgrid=True,
            title=""
        ),
        yaxis=dict(
            gridcolor=COLORS["border"],
            showgrid=True,
            title="Performance (%)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified",
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
