#Universal Asset Dashboard - Quant A

from dash import Dash, html, dcc, callback, Output, Input, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from single_asset.data_fetcher import fetch_data, get_current_price
from single_asset.charts import plot_strategy_normalized
from single_asset.strategies import (
    buy_and_hold, end_of_month, volatility_breakout,
    trend_following, golden_cross, rsi_oversold, macd_crossover
)
from single_asset.metrics import get_all_metrics
import os
import sys

# Allow importing modules from the `portolio_project-main` folder
sys.path.append(os.path.join(os.path.dirname(__file__), "portolio_project-main"))
from utils.data_fetcher import fetch_multiple_assets as fetch_multiple_assets_pm
from utils.data_fetcher import get_current_prices as get_current_prices_pm
from portfolio_module import portfolio_core as pm_core
from portfolio_module import components as pm_components


# render  App 
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server  
app.title = "Portofolio_Project"

#STYLES 
COLORS = {
    "background": "#0a0a0a",
    "card": "#1a1a1a",
    "text": "#ffffff",
    "blue": "#00d4ff",
    "green": "#00ff88",
    "red": "#ff4444",
    "orange": "#ffa500",
    "purple": "#9d4edd",
    "border": "#333333"
}

CARD_STYLE = {
    "backgroundColor": "#000000",
    "padding": "15px",
    "borderRadius": "8px",
    "marginBottom": "15px",
    "border": "1px solid #222"
}



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
app.layout = dcc.Tabs(
    id="main-tabs",
    value="tab-single",
    style={"backgroundColor": "#000000", "color": "#ffffff"},
    children=[
    dcc.Tab(
        label="Single Asset",
        value="tab-single",
        style={"backgroundColor": "#000000", "color": "#ffffff"},
        selected_style={"backgroundColor": "#0a0a0a", "color": "#ffffff", "fontWeight": "bold"},
        children=[
        dbc.Container([
            dcc.Store(id="current-ticker", data="GLE.PA"),
            dcc.Interval(id="refresh-interval", interval=5*60*1000, n_intervals=0),

            # Header
            html.Div([
                html.H1("SINGLE ASSET DASHBOARD", style={
                    "color": "#ffffff",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "margin": "0",
                    "paddingTop": "20px",
                    "paddingBottom": "10px"
                }),
                html.P(id="last-update", style={
                    "color": "#ffffff",
                    "opacity": "0.8",
                    "textAlign": "center",
                    "margin": "0",
                    "paddingBottom": "20px"
                })
            ], style={"backgroundColor": "#000000"}),

            # Sélection Asset
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label("Asset", style={
                            "color": "#ffffff",
                            "marginBottom": "10px"
                        }),
                        dbc.InputGroup([
                            dbc.Input(
                                id="ticker-input",
                                placeholder="Ticker (ex: AAPL, BTC-USD)...",
                                value="GLE.PA",
                                style={
                                    "backgroundColor": "#000000",
                                    "color": "#ffffff",
                                    "border": "1px solid #333"
                                }
                            ),
                            dbc.Button("Charger", id="load-ticker-btn", color="primary")
                        ]),
                        html.Div([
                            dbc.ButtonGroup([
                                dbc.Button("GLE.PA", id="btn-gle", size="sm", outline=True, color="info"),
                                dbc.Button("AAPL", id="btn-aapl", size="sm", outline=True, color="info"),
                                dbc.Button("BTC-USD", id="btn-btc", size="sm", outline=True, color="info"),
                                dbc.Button("TSLA", id="btn-tsla", size="sm", outline=True, color="info"),
                                dbc.Button("SPY", id="btn-spy", size="sm", outline=True, color="info"),
                            ], style={"marginTop": "10px"})
                        ])
                    ], style=CARD_STYLE)
                ], md=4),

                dbc.Col([
                    html.Div(id="price-card", style=CARD_STYLE)
                ], md=4),

                dbc.Col([
                    html.Div(id="asset-info-card", style=CARD_STYLE)
                ], md=4),
            ], style={"marginBottom": "15px"}),

            # Contrôles
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label("Période", style={"color": "#ffffff"}),
                        dcc.Dropdown(
                            id="period-dropdown",
                            options=[
                                {"label": "1 Mois", "value": "1mo"},
                                {"label": "3 Mois", "value": "3mo"},
                                {"label": "6 Mois", "value": "6mo"},
                                {"label": "1 An", "value": "1y"},
                                {"label": "2 Ans", "value": "2y"},
                                {"label": "5 Ans", "value": "5y"}
                            ],
                            value="1y",
                            clearable=False,
                            style={"color": "#000"}
                        )
                    ], style=CARD_STYLE)
                ], md=2),

                dbc.Col([
                    html.Div([
                        html.Label("Strategie", style={"color": "#ffffff"}),
                        dcc.Dropdown(
                            id="strategy-dropdown",
                            options=[
                                {"label": "Buy and Hold", "value": "buy_and_hold"},
                                {"label": "Volatility Breakout", "value": "volatility_breakout"},
                                {"label": "Trend Following", "value": "trend_following"},
                                {"label": "Golden Cross", "value": "golden_cross"},
                                {"label": "RSI Oversold", "value": "rsi_oversold"},
                                {"label": "End of Month", "value": "end_of_month"},
                                {"label": "MACD Crossover", "value": "macd_crossover"}
                            ],
                            value="buy_and_hold",
                            clearable=False,
                            style={"color": "#000"}
                        )
                    ], style=CARD_STYLE)
                ], md=3),

                dbc.Col([
                    html.Div([
                        html.Label("Affichage", style={"color": "#ffffff"}),
                        dcc.Dropdown(
                            id="display-mode-dropdown",
                            options=[
                                {"label": "Base 100 (Performance)", "value": "base100"},
                                {"label": "Rendements % Cumulés", "value": "returns"}
                            ],
                            value="base100",
                            clearable=False,
                            style={"color": "#000"}
                        )
                    ], style=CARD_STYLE)
                ], md=3),

                dbc.Col([
                    html.Div([
                        html.Label("Capital Initial", style={"color": "#ffffff"}),
                        dbc.Input(
                            id="capital-input",
                            type="number",
                            value=10000,
                            style={
                                "backgroundColor": "#000000",
                                "color": "#ffffff",
                                "border": "1px solid #333"
                            }
                        )
                    ], style=CARD_STYLE)
                ], md=2),
            ], style={"marginBottom": "15px"}),

            # Graphique principal
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H5(id="chart-title", style={"color": "#ffffff"}),
                        dcc.Graph(id="main-chart", style={"height": "420px", "backgroundColor": "#000000"})
                    ], style=CARD_STYLE)
                ], md=8),

                dbc.Col([
                    html.Div([
                        html.H5("Performance", style={"color": "#ffffff", "marginBottom": "15px"}),
                        html.Div(id="metrics-display")
                    ], style=CARD_STYLE)
                ], md=4)
            ]),

            # Footer
            html.P("Auto-refresh: 5 min | Quant A Module", style={
                "textAlign": "center",
                "color": "#ffffff",
                "opacity": "0.6",
                "marginTop": "20px"
            })

        ], fluid=True, style={
            "backgroundColor": "#000000",
            "minHeight": "100vh",
            "padding": "20px",
            "color": "#ffffff"
        })
    ]),

    dcc.Tab(label="Portfolio", 
            value="tab-portfolio",
            style={"backgroundColor": "#000000","color": "#ffffff"},
            selected_style={"backgroundColor": "#0a0a0a","color": "#ffffff","fontWeight": "bold"},             
            children=[
        dbc.Container([
            # Use a dedicated interval and store for the portfolio tab (prefixed with pm_)
            dcc.Interval(id="pm_refresh_interval", interval=5*60*1000, n_intervals=0),
            dcc.Store(id="pm_prices_store"),

            # Header
            html.Div([
                html.H1("PORTFOLIO DASHBOARD", style={
                    "color": "#FFFFFF",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "margin": "0",
                    "paddingTop": "20px",
                    "paddingBottom": "10px"
                }),
                html.P(id="pm_last_update", style={
                    "color": "#FFFFFF",
                    "opacity": "0.8",
                    "textAlign": "center",
                    "margin": "0",
                    "paddingBottom": "20px"
                })
            ], style={"backgroundColor": "#000000"}),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label("Assets", style={"color": "#000000"}),
                        dbc.Input(id="pm_assets_input", value=",".join(pm_core.DEFAULT_ASSETS),
                                  style={"backgroundColor": "#000000", "border": "1px solid #333", "color": "#ffffff"})
                    ], style={"padding": "10px", "marginBottom": "10px"})
                ], md=4),
                dbc.Col([
                    html.Div([
                        html.Label("Periode", style={"color": "#ffffff"}),
                        dcc.Dropdown(id="pm_period_dropdown",
                                     options=[{"label": "1 Mois", "value": "1mo"}, {"label": "3 Mois", "value": "3mo"},
                                              {"label": "6 Mois", "value": "6mo"}, {"label": "1 An", "value": "1y"}, {"label": "2 Ans", "value": "2y"}],
                                     value="1y", clearable=False, style={"color": "#000"})
                    ], style={"padding": "10px"})
                ], md=2),
                dbc.Col([
                    html.Div([
                        html.Label("Mode Poids", style={"color": "#ffffff"}),
                        dcc.Dropdown(id="pm_weight_mode", options=[{"label": "Egaux", "value": "equal"}, {"label": "Custom", "value": "custom"}], value="equal", clearable=False, style={"color": "#000"})
                    ], style={"padding": "10px"})
                ], md=2),
                dbc.Col([
                    html.Div([
                        html.Label("Rebalancing", style={"color": "#ffffff"}),
                        dcc.Dropdown(id="pm_rebalancing_freq", options=[{"label": "Jamais", "value": "never"}, {"label": "Mensuel", "value": "monthly"}, {"label": "Trimestriel", "value": "quarterly"}, {"label": "Annuel", "value": "yearly"}], value="never", clearable=False, style={"color": "#000000"})
                    ], style={"padding": "10px"})
                ], md=2),
            ], style={"marginBottom": "15px"}),

            html.Div(id="pm_custom_weights_section"),
            html.Div(id="pm_price_cards", style={"marginBottom": "20px"}),

            # Charts Row 1
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H5("Performance (base 100)", style={"color": "#ffffff"}),
                        dcc.Graph(id="pm_main_chart", style={"height": "420px", "backgroundColor": "#000000"})
                    ], style=CARD_STYLE)
                ], md=8),
                dbc.Col([
                    html.Div([
                        html.H5("Allocation", style={"color": "#ffffff"}),
                        dcc.Graph(id="pm_allocation_chart", style={"height": "420px"})
                    ], style=CARD_STYLE)
                ], md=4)
            ]),

            # Charts Row 2
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H5("Correlation Matrix", style={"color": "#ffffff"}),
                        dcc.Graph(id="pm_correlation_chart", style={"height": "350px"})
                    ], style=CARD_STYLE)
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.H5("Metriques Portfolio", style={"color": "#ffffff"}),
                        html.Div(id="pm_portfolio_metrics")
                    ], style=CARD_STYLE)
                ], md=3),
                dbc.Col([
                    html.Div([
                        html.H5("Metriques Assets", style={"color": "#ffffff"}),
                        html.Div(id="pm_asset_metrics", style={"maxHeight": "300px", "overflowY": "auto"})
                    ], style=CARD_STYLE)
                ], md=3)
            ]),

            html.P("Auto-refresh: 5 min | Quant B Module", style={"textAlign": "center", "color": "#ffffff", "opacity": "0.6", "marginTop": "20px"})

        ], fluid=True, style={"backgroundColor": "#000000", "minHeight": "100vh", "padding": "20px", "color": "#ffffff"})
    ])
])


# CALLBACKS 

@callback(
    Output("current-ticker", "data"),
    Output("ticker-input", "value"),
    Input("load-ticker-btn", "n_clicks"),
    Input("btn-gle", "n_clicks"),
    Input("btn-aapl", "n_clicks"),
    Input("btn-btc", "n_clicks"),
    Input("btn-tsla", "n_clicks"),
    Input("btn-spy", "n_clicks"),
    State("ticker-input", "value")
)
def update_ticker(load_click, gle_click, aapl_click, btc_click, tsla_click, spy_click, input_ticker):
    ctx = callback_context
    if not ctx.triggered:
        return "GLE.PA", "GLE.PA"
    
    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    
    ticker_map = {
        "btn-gle": "GLE.PA",
        "btn-aapl": "AAPL",
        "btn-btc": "BTC-USD",
        "btn-tsla": "TSLA",
        "btn-spy": "SPY"
    }
    
    if trigger in ticker_map:
        ticker = ticker_map[trigger]
        return ticker, ticker
    elif trigger == "load-ticker-btn" and input_ticker:
        ticker = input_ticker.upper().strip()
        return ticker, ticker
    
    return "GLE.PA", "GLE.PA"


@callback(
    Output("last-update", "children"),
    Input("refresh-interval", "n_intervals")
)
def update_timestamp(n):
    return f"Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"


@callback(
    Output("price-card", "children"),
    Output("asset-info-card", "children"),
    Input("current-ticker", "data"),
    Input("refresh-interval", "n_intervals")
)
def update_info_cards(ticker, n):
    try:
        info = get_current_price(ticker)
        is_positive = info["change"] >= 0
        color = COLORS["green"] if is_positive else COLORS["red"]
        arrow = "▲" if is_positive else "▼"
        
        price_card = [
            html.H6("Prix Actuel", style={"color": "#ffffff", "opacity": "0.8", "fontSize": "14px", "marginBottom": "10px"}),
            html.H4(f"{info['price']:.2f} {info['currency']}", style={"color": "#ffffff", "marginBottom": "5px"}),
            html.Span(f"{arrow} {info['change']:+.2f}%", style={
                "color": color,
                "fontWeight": "bold",
                "fontSize": "16px"
            })
        ]
        
        info_card = [
            html.H6("Informations", style={"color": "#ffffff", "opacity": "0.8", "fontSize": "14px", "marginBottom": "10px"}),
            html.P([
                html.Span("Nom: ", style={"color": "#ffffff", "opacity": "0.7"}),
                html.Span(info['name'], style={"color": "#ffffff"})
            ], style={"margin": "5px 0", "fontSize": "14px"}),
            html.P([
                html.Span("Ticker: ", style={"color": "#ffffff", "opacity": "0.7"}),
                html.Span(info['ticker'], style={"color": "#ffffff"})
            ], style={"margin": "5px 0", "fontSize": "14px"}),
            html.P([
                html.Span("Exchange: ", style={"color": "#ffffff", "opacity": "0.7"}),
                html.Span(info['exchange'], style={"color": "#ffffff"})
            ], style={"margin": "5px 0", "fontSize": "14px"})
        ]
        
        return price_card, info_card
        
    except Exception as e:
        error_msg = [
            html.H6("Erreur", style={"color": COLORS["red"]}),
            html.P(f"Impossible de charger {ticker}", style={"color": "#ffffff", "opacity": "0.7"}),
            html.P(str(e), style={"color": COLORS["red"], "fontSize": "12px", "opacity": "0.7"})
        ]
        return error_msg, error_msg


@callback(
    Output("main-chart", "figure"),
    Output("metrics-display", "children"),
    Output("chart-title", "children"),
    Input("current-ticker", "data"),
    Input("period-dropdown", "value"),
    Input("strategy-dropdown", "value"),
    Input("capital-input", "value"),
    Input("display-mode-dropdown", "value"),
    Input("refresh-interval", "n_intervals")
)
def update_charts(ticker, period, strategy, capital, display_mode, n):
    try:
        capital = capital or 10000
        data = fetch_data(ticker, period)
        
        # Appliquer la stratégie
        result = STRATEGIES[strategy](data, initial_capital=capital)
        
        # Nom de la stratégie pour le titre
        strategy_names = {
            "buy_and_hold": "Buy and Hold",
            "volatility_breakout": "Volatility Breakout",
            "trend_following": "Trend Following",
            "golden_cross": "Golden Cross",
            "rsi_oversold": "RSI Oversold",
            "end_of_month": "End of Month",
            "macd_crossover": "MACD Crossover"
        }
        
        chart_title = f"{ticker} - {strategy_names[strategy]}"
        
        # Graphique avec normalisation
        main_fig = plot_strategy_normalized(
            data=data,
            result=result,
            ticker=ticker,
            strategy_name=strategy_names[strategy],
            colors=COLORS,
            display_mode=display_mode
        )
        
        # Métriques
        metrics = get_all_metrics(result)
        metrics_rows = []
        
        metric_labels = {
            "Total Return": "Return Total",
            "Sharpe Ratio": "Sharpe Ratio",
            "Max Drawdown": "Max Drawdown",
            "Calmar Ratio": "Calmar Ratio"
        }
        
        for name, value in metrics.items():
            if "Return" in name or "Drawdown" in name:
                color = COLORS["green"] if value >= 0 else COLORS["red"]
            elif "Sharpe" in name or "Calmar" in name:
                if value >= 2:
                    color = COLORS["green"]
                elif value >= 1:
                    color = COLORS["orange"]
                else:
                    color = COLORS["red"]
            else:
                color = "#ffffff"
            
            display_name = metric_labels.get(name, name)
            
            metrics_rows.append(
                html.Div([
                    html.Span(f"{display_name}", style={
                        "color": "#ffffff",
                        "opacity": "0.8",
                        "fontSize": "14px"
                    }),
                    html.Span(f"{value}", style={
                        "color": color,
                        "fontWeight": "bold",
                        "float": "right",
                        "fontSize": "16px"
                    })
                ], style={
                    "marginBottom": "15px",
                    "paddingBottom": "10px",
                    "borderBottom": "1px solid #222"
                })
            )
        
        return main_fig, html.Div(metrics_rows), chart_title
        
    except Exception as e:
        error_fig = go.Figure()
        error_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            annotations=[{
                "text": f"Erreur: {str(e)}",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 20, "color": COLORS["red"]}
            }]
        )
        
        error_metrics = html.P("Erreur de chargement", style={"color": COLORS["red"]})
        return error_fig, error_metrics, f"Erreur - {ticker}"


@callback(Output("pm_last_update", "children"), Input("pm_refresh_interval", "n_intervals"))
def pm_update_timestamp(n):
    return f"Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"


@callback(Output("pm_price_cards", "children"), Input("pm_assets_input", "value"), Input("pm_refresh_interval", "n_intervals"))
def pm_update_price_cards(assets_str, n):
    if not assets_str:
        return html.P("Entrez des assets", style={"color": "#ffffff"})
    assets = [a.strip().upper() for a in assets_str.split(",") if a.strip()]
    try:
        prices = get_current_prices_pm(assets)
    except Exception:
        return html.P("Erreur lors de la récupération des prix", style={"color": "#ff4444"})

    cards = []
    for ticker, info in prices.items():
        is_positive = info.get("change", 0) >= 0
        change_color = pm_components.COLORS.get("green", "#00ff88") if is_positive else pm_components.COLORS.get("red", "#ff6b6b")
        arrow = "▲" if is_positive else "▼"
        card = dbc.Col([
            html.Div([
                html.H6(ticker, style={"color": "#ffffff", "opacity": "0.8", "fontSize": "12px"}),
                html.H4(f"{info.get('price', 0):.2f}", style={"color": "#ffffff"}),
                html.Span(f"{arrow} {info.get('change', 0):+.2f}%", style={"color": change_color, "fontWeight": "bold"})
            ], style={"backgroundColor": "#0a0a0a", "padding": "12px", "borderRadius": "6px", "border": "1px solid #222"})
        ], md=2)
        cards.append(card)
    return dbc.Row(children=cards)


@callback(
    Output("pm_main_chart", "figure"), Output("pm_correlation_chart", "figure"), Output("pm_allocation_chart", "figure"),
    Output("pm_portfolio_metrics", "children"), Output("pm_asset_metrics", "children"),
    Input("pm_assets_input", "value"), Input("pm_period_dropdown", "value"), Input("pm_weight_mode", "value"), Input("pm_refresh_interval", "n_intervals")
)
def pm_update_all(assets_str, period, weight_mode, n):
    empty = go.Figure()
    empty.update_layout(template="plotly_dark", paper_bgcolor="#000000", plot_bgcolor="#000000")

    if not assets_str:
        return empty, empty, empty, html.P("Pas de données", style={"color": "#ffffff"}), html.P("", style={"color": "#ffffff"})

    assets = [a.strip().upper() for a in assets_str.split(",") if a.strip()]
    df = fetch_multiple_assets_pm(assets, period)

    if df.empty:
        empty.add_annotation(text="Aucune donnée", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return empty, empty, empty, html.P("Pas de données", style={"color": "#ffffff"}), html.P("Pas de données", style={"color": "#ffffff"})

    # We only support equal weights for now
    weights = pm_core.create_equal_weights(list(df.columns))

    analysis = pm_core.analyze_portfolio(df, weights)

    # Main chart (normalized)
    df_norm = (df / df.iloc[0]) * 100
    main_fig = pm_components.create_main_chart(df_norm, analysis["portfolio_value"], pm_components.COLORS)

    # Correlation
    corr_fig = pm_components.create_correlation_heatmap(analysis["correlation"])

    # Allocation pie
    alloc_fig = pm_components.create_weights_pie_chart({k: v * 100 for k, v in weights.items()})

    # Portfolio metrics card
    portfolio_metrics = pm_components.create_portfolio_metrics_card(analysis["portfolio"])

    # Asset metrics list
    am = analysis["assets"]
    asset_rows = []
    for asset, data in am.items():
        ret_col = pm_components.COLORS["green"] if data["return"] >= 0 else pm_components.COLORS["red"]
        asset_rows.append(html.Div([
            html.Span(f"{asset}", style={"color": "#ffffff", "fontWeight": "bold", "marginRight": "10px"}),
            html.Span(f"R:{data['return']}%", style={"color": ret_col, "marginRight": "8px"}),
            html.Span(f"Vol:{data['volatility']}%", style={"color": pm_components.COLORS['orange'], "marginRight": "8px"}),
            html.Span(f"Sharpe:{data['sharpe']}", style={"color": pm_components.COLORS['blue']})
        ], style={"marginBottom": "10px", "padding": "8px", "backgroundColor": "#000000", "borderRadius": "4px"}))

    return main_fig, corr_fig, alloc_fig, portfolio_metrics, html.Div(asset_rows)


if __name__ == "__main__":
    app.run(debug=True)