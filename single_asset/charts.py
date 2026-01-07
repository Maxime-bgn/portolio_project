import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def plot_price(data: pd.DataFrame):
    # Plot underlying asset price time-series
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name="Asset Price",
        line=dict(color="#00d4ff", width=2)
    ))
    fig.update_layout(
        title="Société Générale Price (GLE.PA)",
        xaxis_title="Date",
        yaxis_title="Price (€)",
        template="plotly_dark"
    )
    return fig


def plot_strategy_normalized(data: pd.DataFrame, result: pd.DataFrame, 
                             ticker: str, strategy_name: str,
                             colors: dict = None, display_mode: str = "base100"):
    # Plot price vs strategy normalized or raw values
    if colors is None:
        colors = {
            "blue": "#00d4ff",
            "green": "#00ff88",
            "card": "#1a1a1a",
            "text": "#ffffff",
            "orange": "#ffa500"
        }

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if display_mode == "base100":
        # Base 100 normalization for price and portfolio
        price_norm = (data["Close"] / data["Close"].iloc[0]) * 100
        portfolio_norm = (result["portfolio_value"] / result["portfolio_value"].iloc[0]) * 100

        fig.add_trace(
            go.Scatter(x=data.index, y=price_norm,
                       name=f"Price {ticker}",
                       line=dict(color=colors["orange"], width=2.5)),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(x=result.index, y=portfolio_norm,
                       name=f"Strategy {strategy_name}",
                       line=dict(color=colors["green"], width=2.5)),
            secondary_y=True
        )

        fig.update_yaxes(title_text="Asset Price (Base 100)", secondary_y=False)
        fig.update_yaxes(title_text="Portfolio (Base 100)", secondary_y=True)

    else:
        # Raw price and portfolio values
        fig.add_trace(
            go.Scatter(x=data.index, y=data["Close"],
                       name=f"Price {ticker} (EUR)",
                       line=dict(color=colors["orange"], width=2.5)),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(x=result.index, y=result["portfolio_value"],
                       name=f"Portfolio {strategy_name} (EUR)",
                       line=dict(color=colors["green"], width=2.5)),
            secondary_y=True
        )

        fig.update_yaxes(title_text=f"Price {ticker} (€)", secondary_y=False)
        fig.update_yaxes(title_text="Portfolio Value (€)", secondary_y=True)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=colors["card"],
        plot_bgcolor=colors["card"],
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(title="Date", color=colors["text"])
    )

    return fig


def plot_strategy(data: pd.DataFrame, strategy_name: str = "Strategy"):
    # Plot underlying price and portfolio value on 2 subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Asset Price", f"Portfolio - {strategy_name}")
    )

    fig.add_trace(go.Scatter(
        x=data.index, y=data["Close"],
        mode="lines", name="Price",
        line=dict(color="#00d4ff", width=2)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=data.index, y=data["portfolio_value"],
        mode="lines", name="Portfolio",
        line=dict(color="#00ff88", width=2)
    ), row=2, col=1)

    fig.update_layout(
        height=600,
        template="plotly_dark",
        showlegend=True
    )
    return fig


def plot_compare_strategies(results: dict, initial_capital: float = 10000, 
                            normalize: bool = True):
    # Compare multiple strategies on the same chart
    fig = go.Figure()

    colors = ["#00d4ff", "#00ff88", "#ff6b6b", "#ffd93d", "#9d4edd", "#ff9f1c"]

    for i, (name, data) in enumerate(results.items()):
        if normalize:
            values = (data["portfolio_value"] / data["portfolio_value"].iloc[0]) * 100
            yaxis_title = "Performance (Base 100)"
        else:
            values = data["portfolio_value"]
            yaxis_title = "Portfolio Value (€)"

        fig.add_trace(go.Scatter(
            x=data.index,
            y=values,
            mode="lines",
            name=name,
            line=dict(color=colors[i % len(colors)], width=2)
        ))

    reference_value = 100 if normalize else initial_capital

    fig.add_hline(
        y=reference_value,
        line_dash="dash",
        line_color="white",
        opacity=0.5,
        annotation_text=f"Reference ({reference_value})"
    )

    fig.update_layout(
        title="Strategy Comparison",
        xaxis_title="Date",
        yaxis_title=yaxis_title,
        template="plotly_dark",
        hovermode="x unified"
    )
    return fig


def plot_drawdown(data: pd.DataFrame):
    # Compute drawdown and plot it as filled area
    df = data.copy()
    df["peak"] = df["portfolio_value"].expanding().max()
    df["drawdown"] = (df["portfolio_value"] - df["peak"]) / df["peak"] * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["drawdown"],
        fill="tozeroy",
        mode="lines",
        name="Drawdown",
        line=dict(color="#ff6b6b", width=1)
    ))

    fig.update_layout(
        title="Drawdown (%)",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_dark"
    )
    return fig


def plot_returns_distribution(data: pd.DataFrame):
    # Histogram of daily % returns
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=data["returns"].dropna() * 100,
        nbinsx=50,
        name="Returns",
        marker_color="#00d4ff"
    ))

    fig.update_layout(
        title="Daily Return Distribution",
        xaxis_title="Return (%)",
        yaxis_title="Frequency",
        template="plotly_dark"
    )
    return fig
