"""
Portfolio Dashboard - Multi-Page Application
Pages: Portfolio | Advanced Analytics
"""

from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

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

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
app.title = "Portfolio Analytics | Quant B"
server = app.server

REFRESH_INTERVAL = 5 * 60 * 1000

# Navigation
def create_navbar():
    return dbc.Nav([
        dbc.NavItem(dbc.NavLink("PORTFOLIO", href="#", id="nav-portfolio", active=True, 
                               style={"color": COLORS["text"], "fontWeight": "600"})),
        dbc.NavItem(dbc.NavLink("ADVANCED ANALYTICS", href="#", id="nav-advanced",
                               style={"color": COLORS["text"], "fontWeight": "600"})),
    ], pills=True, style={"marginBottom": "20px"})


app.layout = dbc.Container([
    dcc.Interval(id="refresh-interval", interval=REFRESH_INTERVAL, n_intervals=0),
    dcc.Store(id="current-page", data="portfolio"),
    dcc.Store(id="prices-data"),
    dcc.Store(id="weights-data"),
    
    # Header
    html.Div([
        html.Div([
            html.H1("PORTFOLIO ANALYTICS", 
                    style={
                        "color": COLORS["text"],
                        "fontWeight": "700",
                        "fontSize": "28px",
                        "marginBottom": "4px",
                        "letterSpacing": "-0.5px"
                    }),
            html.P("Multi-Asset Portfolio Management & Risk Analysis", 
                   style={
                       "color": COLORS["text_secondary"],
                       "fontSize": "14px",
                       "marginBottom": "8px"
                   }),
            html.P(id="last-update", 
                   style={
                       "color": COLORS["positive"],
                       "fontSize": "11px",
                       "fontWeight": "500"
                   })
        ])
    ], style={
        "borderBottom": f"1px solid {COLORS['border']}",
        "padding": "24px 0",
        "marginBottom": "24px"
    }),
    
    # Navigation
    create_navbar(),
    
    # Controls
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label("Assets (tickers)", style={"color": COLORS["text"]}),
                    dbc.Input(
                        id="assets-input", 
                        value=", ".join(DEFAULT_ASSETS),
                        style={"backgroundColor": COLORS["card"], "color": COLORS["text"]}
                    )
                ], style=CARD_STYLE)
            ], md=4),
            
            dbc.Col([
                html.Div([
                    html.Label("Periode", style={"color": COLORS["text"]}),
                    dcc.Dropdown(
                        id="period-dropdown",
                        options=[
                            {"label": "1 Mois", "value": "1mo"},
                            {"label": "3 Mois", "value": "3mo"},
                            {"label": "6 Mois", "value": "6mo"},
                            {"label": "1 An", "value": "1y"},
                            {"label": "2 Ans", "value": "2y"}
                        ],
                        value="1y",
                        clearable=False
                    )
                ], style=CARD_STYLE)
            ], md=2),
            
            dbc.Col([
                html.Div([
                    html.Label("Mode Poids", style={"color": COLORS["text"]}),
                    dcc.Dropdown(
                        id="weight-mode",
                        options=[
                            {"label": "Egaux", "value": "equal"},
                            {"label": "Custom", "value": "custom"}
                        ],
                        value="equal",
                        clearable=False
                    )
                ], style=CARD_STYLE)
            ], md=2),
            
            dbc.Col([
                html.Div([
                    html.Label("Rebalancing", style={"color": COLORS["text"]}),
                    dcc.Dropdown(
                        id="rebalancing-freq",
                        options=[
                            {"label": "Jamais", "value": "never"},
                            {"label": "Mensuel", "value": "monthly"},
                            {"label": "Trimestriel", "value": "quarterly"}
                        ],
                        value="never",
                        clearable=False
                    )
                ], style=CARD_STYLE)
            ], md=2),
            
            dbc.Col([
                html.Div([
                    html.Label("Benchmark", style={"color": COLORS["text"]}),
                    dbc.Input(
                        id="benchmark-input",
                        value="SPY",
                        placeholder="Ex: SPY",
                        style={"backgroundColor": COLORS["card"], "color": COLORS["text"]}
                    )
                ], style=CARD_STYLE)
            ], md=2)
        ]),
        
        html.Div([
            html.Label("Poids Custom (%)", style={"color": COLORS["text"]}),
            dbc.Input(
                id="weights-input",
                value="20, 20, 20, 20, 20",
                placeholder="Ex: 30, 25, 20, 15, 10",
                style={"backgroundColor": COLORS["card"], "color": COLORS["text"]}
            )
        ], style=CARD_STYLE, id="custom-weights-section"),
        
    ]),
    
    # Page content
    html.Div(id="page-content"),
    
    # Footer
    html.Div([
        html.P([
            html.Span("Auto-refresh: 5 minutes", style={"marginRight": "20px"}),
            html.Span("•", style={"marginRight": "20px", "opacity": "0.3"}),
            html.Span("Quant B Module", style={"marginRight": "20px"}),
            html.Span("•", style={"marginRight": "20px", "opacity": "0.3"}),
            html.Span("Professional Portfolio Analytics")
        ], style={
            "textAlign": "center",
            "color": COLORS["text_secondary"],
            "fontSize": "11px",
            "opacity": "0.7",
            "marginTop": "32px",
            "paddingTop": "24px",
            "borderTop": f"1px solid {COLORS['border']}"
        })
    ])
    
], fluid=True, style={"backgroundColor": COLORS["background"], 
                      "minHeight": "100vh", "padding": "20px"})


# Callbacks for navigation
@callback(
    Output("current-page", "data"),
    Output("nav-portfolio", "active"),
    Output("nav-advanced", "active"),
    Input("nav-portfolio", "n_clicks"),
    Input("nav-advanced", "n_clicks"),
    State("current-page", "data")
)
def navigate(port_clicks, adv_clicks, current):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "portfolio", True, False
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "nav-portfolio":
        return "portfolio", True, False
    elif button_id == "nav-advanced":
        return "advanced", False, True
    
    return current, current == "portfolio", current == "advanced"


@callback(
    Output("last-update", "children"),
    Input("refresh-interval", "n_intervals")
)
def update_timestamp(n):
    return f"Mis a jour: {datetime.now().strftime('%H:%M:%S')}"


@callback(
    Output("custom-weights-section", "style"),
    Input("weight-mode", "value")
)
def toggle_custom_weights(mode):
    style = CARD_STYLE.copy()
    if mode == "custom":
        style["display"] = "block"
    else:
        style["display"] = "none"
    return style


@callback(
    Output("page-content", "children"),
    Input("current-page", "data"),
    Input("assets-input", "value"),
    Input("period-dropdown", "value"),
    Input("weights-input", "value"),
    Input("weight-mode", "value"),
    Input("rebalancing-freq", "value"),
    Input("benchmark-input", "value"),
    Input("refresh-interval", "n_intervals")
)
def render_page(page, assets_str, period, weights_str, weight_mode, rebalancing, benchmark_str, n):
    if page == "portfolio":
        return render_portfolio_page(assets_str, period, weights_str, weight_mode, rebalancing, benchmark_str)
    elif page == "advanced":
        return render_advanced_page(assets_str, period, weights_str, weight_mode)
    
    return html.Div("Page not found")


def render_portfolio_page(assets_str, period, weights_str, weight_mode, rebalancing, benchmark_str):
    """Render the main portfolio page"""
    
    empty = html.Div("Enter assets to begin", style={"color": COLORS["text"], "padding": "40px", "textAlign": "center"})
    
    if not assets_str:
        return empty
    
    # Parse assets
    assets = [a.strip().upper() for a in assets_str.split(",") if a.strip()]
    
    # Fetch data
    df = fetch_multiple_assets(assets, period)
    if df.empty:
        return html.Div("No data available", style={"color": COLORS["text"], "padding": "40px", "textAlign": "center"})
    
    # Weights
    if weight_mode == "equal":
        weights = create_equal_weights(df.columns.tolist())
    else:
        try:
            weight_values = [float(w.strip()) for w in weights_str.split(",")]
            if len(weight_values) != len(df.columns):
                weight_values = [100 / len(df.columns)] * len(df.columns)
        except:
            weight_values = [100 / len(df.columns)] * len(df.columns)
        
        total = sum(weight_values)
        weights = {asset: w / total for asset, w in zip(df.columns, weight_values)}
    
    # Benchmark
    market_returns = None
    if benchmark_str and benchmark_str.strip():
        try:
            benchmark_df = fetch_multiple_assets([benchmark_str.strip().upper()], period)
            if not benchmark_df.empty:
                market_returns = calculate_returns(benchmark_df).iloc[:, 0]
        except:
            pass
    
    # Calculate
    port_value_series = portfolio_value(df, weights, rebalancing_freq=rebalancing)
    analysis = analyze_portfolio(df, weights, market_returns=market_returns)
    analysis["portfolio_value"] = port_value_series
    
    # Create charts
    df_norm = (df / df.iloc[0]) * 100
    main_fig = create_main_chart(df_norm, analysis["portfolio_value"], COLORS)
    corr_fig = create_correlation_heatmap(analysis["correlation"])
    alloc_fig = create_weights_pie_chart(weights)
    drawdown_fig = create_drawdown_chart(analysis["portfolio_value"])
    
    # Portfolio metrics
    portfolio_metrics = create_portfolio_metrics_card(analysis["portfolio"])
    
    # Asset metrics table
    am = analysis["assets"]
    asset_rows = []
    for asset, data in am.items():
        ret_col = COLORS["positive"] if data["return"] >= 0 else COLORS["negative"]
        
        row = html.Tr([
            html.Td(asset, style={"color": COLORS["accent"], "fontWeight": "bold"}),
            html.Td(f"{data['return']}%", style={"color": ret_col}),
            html.Td(f"{data['volatility']}%", style={"color": COLORS["warning"]}),
            html.Td(f"{data['sharpe']}", style={"color": COLORS["accent"]}),
            html.Td(f"{data['weight']}%", style={"color": COLORS["positive"]})
        ])
        asset_rows.append(row)
    
    asset_table = html.Table([
        html.Thead(html.Tr([
            html.Th("Asset", style={"color": COLORS["text"]}),
            html.Th("Return", style={"color": COLORS["text"]}),
            html.Th("Vol", style={"color": COLORS["text"]}),
            html.Th("Sharpe", style={"color": COLORS["text"]}),
            html.Th("Weight", style={"color": COLORS["text"]})
        ])),
        html.Tbody(asset_rows)
    ], style={"width": "100%", "color": COLORS["text"]})
    
    # Price cards
    prices = get_current_prices(assets)
    price_cards = []
    for ticker, info in prices.items():
        is_positive = info["change"] >= 0
        change_color = COLORS["positive"] if is_positive else COLORS["negative"]
        arrow = "▲" if is_positive else "▼"
        
        card = dbc.Col([
            html.Div([
                html.Div([
                    html.Span(ticker, style={
                        "color": COLORS["accent"],
                        "fontWeight": "700",
                        "fontSize": "11px",
                        "letterSpacing": "0.5px"
                    }),
                ], style={"marginBottom": "8px"}),
                html.Div([
                    html.Span(f"${info['price']:.2f}", style={
                        "color": COLORS["text"],
                        "fontSize": "22px",
                        "fontWeight": "600"
                    }),
                ], style={"marginBottom": "6px"}),
                html.Div([
                    html.Span(f"{arrow} ", style={
                        "color": change_color,
                        "fontSize": "10px",
                        "marginRight": "2px"
                    }),
                    html.Span(f"{abs(info['change']):.2f}%", style={
                        "color": change_color,
                        "fontWeight": "600",
                        "fontSize": "13px"
                    })
                ])
            ], style={
                **CARD_STYLE,
                "minHeight": "110px",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "space-between"
            })
        ], md=2, sm=4, xs=6)
        price_cards.append(card)
    
    return html.Div([
        # Price cards
        html.Div(dbc.Row(children=price_cards), style={"marginBottom": "20px"}),
        
        # Main charts
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("PERFORMANCE (BASE 100)", style={
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "textTransform": "uppercase",
                        "marginBottom": "16px"
                    }),
                    dcc.Graph(figure=main_fig, style={"height": "400px"})
                ], style=CARD_STYLE)
            ], md=8),
            
            dbc.Col([
                html.Div([
                    html.H5("ALLOCATION", style={
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "textTransform": "uppercase",
                        "marginBottom": "16px"
                    }),
                    dcc.Graph(figure=alloc_fig, style={"height": "400px"})
                ], style=CARD_STYLE)
            ], md=4)
        ]),
        
        # Secondary charts
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("DRAWDOWN ANALYSIS", style={
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "textTransform": "uppercase",
                        "marginBottom": "16px"
                    }),
                    dcc.Graph(figure=drawdown_fig, style={"height": "300px"})
                ], style=CARD_STYLE)
            ], md=6),
            
            dbc.Col([
                html.Div([
                    html.H5("CORRELATION MATRIX", style={
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "textTransform": "uppercase",
                        "marginBottom": "16px"
                    }),
                    dcc.Graph(figure=corr_fig, style={"height": "300px"})
                ], style=CARD_STYLE)
            ], md=6)
        ]),
        
        # Metrics
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("PORTFOLIO METRICS", style={
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "textTransform": "uppercase",
                        "marginBottom": "16px"
                    }),
                    portfolio_metrics
                ], style=CARD_STYLE)
            ], md=5),
            
            dbc.Col([
                html.Div([
                    html.H5("ASSET BREAKDOWN", style={
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "textTransform": "uppercase",
                        "marginBottom": "16px"
                    }),
                    asset_table
                ], style=CARD_STYLE)
            ], md=7)
        ]),
    ])


def render_advanced_page(assets_str, period, weights_str, weight_mode):
    """Render the advanced analytics page"""
    
    if not assets_str:
        return html.Div("Configure portfolio first", style={"color": COLORS["text"], "padding": "40px", "textAlign": "center"})
    
    assets = [a.strip().upper() for a in assets_str.split(",") if a.strip()]
    df = fetch_multiple_assets(assets, period)
    
    if df.empty:
        return html.Div("No data", style={"color": COLORS["text"], "padding": "40px", "textAlign": "center"})
    
    # Parse weights
    if weight_mode == "equal":
        weights = create_equal_weights(df.columns.tolist())
    else:
        try:
            weight_values = [float(w.strip()) for w in weights_str.split(",")]
            if len(weight_values) != len(df.columns):
                weight_values = [100 / len(df.columns)] * len(df.columns)
        except:
            weight_values = [100 / len(df.columns)] * len(df.columns)
        
        total = sum(weight_values)
        weights = {asset: w / total for asset, w in zip(df.columns, weight_values)}
    
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
    fig_msv.add_trace(go.Scatter(
        x=msv['scale'],
        y=msv['annualized_vol'],
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
        yaxis=dict(title="Annualized Volatility (%)")
    )
    
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
    
    for regime_name in ['Bull', 'Bear', 'High Vol', 'Sideways']:
        regime_mask = regimes == regime_name
        if regime_mask.sum() > 0:
            fig_regimes.add_trace(go.Scatter(
                x=port_prices.index[regime_mask],
                y=port_prices[regime_mask],
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
    
    vr_table_rows = []
    for _, row in vr_test.iterrows():
        color = COLORS["positive"] if row['interpretation'] == 'Random Walk' else COLORS["warning"]
        vr_table_rows.append(html.Tr([
            html.Td(f"{row['lag']} days", style={"color": COLORS["text"]}),
            html.Td(f"{row['variance_ratio']:.3f}", style={"color": color}),
            html.Td(f"{row['z_statistic']:.2f}", style={"color": COLORS["text_secondary"]}),
            html.Td(row['interpretation'], style={"color": color, "fontWeight": "bold"})
        ]))
    
    vr_table = html.Table([
        html.Thead(html.Tr([
            html.Th("Lag", style={"color": COLORS["text"]}),
            html.Th("VR", style={"color": COLORS["text"]}),
            html.Th("Z-stat", style={"color": COLORS["text"]}),
            html.Th("Interpretation", style={"color": COLORS["text"]})
        ])),
        html.Tbody(vr_table_rows)
    ], style={"width": "100%", "color": COLORS["text"]})
    
    # Interpretation card
    interpretation_text = f"""
    Portfolio Hurst Exponent: {H_portfolio:.3f}
    
    Interpretation:
    - H > 0.55: Persistent (trending behavior, momentum)
    - H = 0.50: Random walk (efficient market)
    - H < 0.45: Anti-persistent (mean-reverting)
    
    Your portfolio shows {"PERSISTENT" if H_portfolio > 0.55 else "RANDOM WALK" if 0.45 <= H_portfolio <= 0.55 else "ANTI-PERSISTENT"} behavior.
    """
    
    return html.Div([
        # Header with explanation
        html.Div([
            html.H4("ADVANCED ANALYTICS", style={
                "color": COLORS["text"],
                "fontSize": "18px",
                "fontWeight": "700",
                "marginBottom": "8px"
            }),
            html.P("Multi-scale analysis based on ESILV Market Risk course", style={
                "color": COLORS["text_secondary"],
                "fontSize": "12px",
                "marginBottom": "20px"
            })
        ]),
        
        # Hurst Exponent
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("HURST EXPONENT BY ASSET", style={
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "textTransform": "uppercase",
                        "marginBottom": "16px"
                    }),
                    dcc.Graph(figure=fig_hurst, style={"height": "350px"})
                ], style=CARD_STYLE)
            ], md=8),
            
            dbc.Col([
                html.Div([
                    html.H5("INTERPRETATION", style={
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "textTransform": "uppercase",
                        "marginBottom": "16px"
                    }),
                    html.Pre(interpretation_text, style={
                        "color": COLORS["text"],
                        "fontSize": "11px",
                        "whiteSpace": "pre-wrap",
                        "fontFamily": "monospace"
                    })
                ], style=CARD_STYLE)
            ], md=4)
        ]),
        
        # Multi-scale variance
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("MULTI-SCALE VARIANCE", style={
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "textTransform": "uppercase",
                        "marginBottom": "16px"
                    }),
                    dcc.Graph(figure=fig_msv, style={"height": "350px"})
                ], style=CARD_STYLE)
            ], md=6),
            
            dbc.Col([
                html.Div([
                    html.H5("VARIANCE RATIO TEST", style={
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "textTransform": "uppercase",
                        "marginBottom": "16px"
                    }),
                    vr_table,
                    html.P("Lo-MacKinlay test for random walk hypothesis", style={
                        "color": COLORS["text_secondary"],
                        "fontSize": "10px",
                        "marginTop": "12px"
                    })
                ], style=CARD_STYLE)
            ], md=6)
        ]),
        
        # Regime detection
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("REGIME DETECTION", style={
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "textTransform": "uppercase",
                        "marginBottom": "16px"
                    }),
                    dcc.Graph(figure=fig_regimes, style={"height": "400px"}),
                    html.P("Simple regime classification based on rolling statistics", style={
                        "color": COLORS["text_secondary"],
                        "fontSize": "10px",
                        "marginTop": "12px"
                    })
                ], style=CARD_STYLE)
            ], md=12)
        ]),
    ])


if __name__ == '__main__':
    app.run(debug=True)
