# Performance charts - Plotly

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def plot_price(data: pd.DataFrame):
    # Chart of the asset price
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name='SG Price',
        line=dict(color='#00d4ff', width=2)
    ))
    fig.update_layout(
        title="Société Générale Price (GLE.PA)",
        xaxis_title="Date",
        yaxis_title="Price (€)",
        template="plotly_dark"
    )
    return fig


def plot_strategy_normalized(data: pd.DataFrame, result: pd.DataFrame, ticker: str, strategy_name: str, colors: dict = None, display_mode: str = "base100"):
    # Normalized chart: Price vs Strategy with double Y-axis
    
    if colors is None:
        colors = {
            "blue": "#00d4ff",
            "green": "#00ff88",
            "card": "#1a1a1a",
            "text": "#ffffff",
            "orange": "#ffa500"
        }
    
    # Create subplot with secondary_y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if display_mode == "base100":
        # Base 100 normalization
        price_norm = (data['Close'] / data['Close'].iloc[0]) * 100
        portfolio_norm = (result['portfolio_value'] / result['portfolio_value'].iloc[0]) * 100
        
        fig.add_trace(
            go.Scatter(x=data.index, y=price_norm,
                      name=f"{ticker} Price",
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
        
    else:  # "returns" mode
        # Raw price vs portfolio value
        fig.add_trace(
            go.Scatter(x=data.index, y=data['Close'],
                      name=f"{ticker} Price (EUR)",
                      line=dict(color=colors["orange"], width=2.5)),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=result.index, y=result['portfolio_value'],
                      name=f"Portfolio {strategy_name} (EUR)",
                      line=dict(color=colors["green"], width=2.5)),
            secondary_y=True
        )
        
        fig.update_yaxes(title_text=f"{ticker} Price (€)", secondary_y=False)
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
    # Chart price + portfolio value
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("SG Price", f"Portfolio - {strategy_name}")
    )
    
    # Price
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'],
        mode='lines', name='Price',
        line=dict(color='#00d4ff', width=2)
    ), row=1, col=1)
    
    # Portfolio value
    fig.add_trace(go.Scatter(
        x=data.index, y=data['portfolio_value'],
        mode='lines', name='Portfolio',
        line=dict(color='#00ff88', width=2)
    ), row=2, col=1)
    
    fig.update_layout(
        height=600,
        template="plotly_dark",
        showlegend=True
    )
    return fig


def plot_compare_strategies(results: dict, initial_capital: float = 10000, normalize: bool = True):
    # Compare several strategies on the same chart
    """
    Args:
        results: dict with {strategy_name: DataFrame}
        initial_capital: starting capital
        normalize: if True, normalize all lines to base 100
    """
    fig = go.Figure()
    
    colors = ['#00d4ff', '#00ff88', '#ff6b6b', '#ffd93d', '#9d4edd', '#ff9f1c']
    
    for i, (name, data) in enumerate(results.items()):
        if normalize:
            # Base 100 normalization
            values = (data['portfolio_value'] / data['portfolio_value'].iloc[0]) * 100
            yaxis_title = "Performance (Base 100)"
        else:
            values = data['portfolio_value']
            yaxis_title = "Portfolio Value (€)"
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=values,
            mode='lines',
            name=name,
            line=dict(color=colors[i % len(colors)], width=2)
        ))
    
    # Reference line
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
    # Drawdown chart
    df = data.copy()
    df['peak'] = df['portfolio_value'].expanding().max()
    df['drawdown'] = (df['portfolio_value'] - df['peak']) / df['peak'] * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['drawdown'],
        fill='tozeroy',
        mode='lines',
        name='Drawdown',
        line=dict(color='#ff6b6b', width=1)
    ))
    
    fig.update_layout(
        title="Drawdown (%)",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_dark"
    )
    return fig


def plot_returns_distribution(data: pd.DataFrame):
    # Histogram of daily returns
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=data['returns'].dropna() * 100,
        nbinsx=50,
        name='Returns',
        marker_color='#00d4ff'
    ))
    
    fig.update_layout(
        title="Daily Return Distribution",
        xaxis_title="Return (%)",
        yaxis_title="Frequency",
        template="plotly_dark"
    )
    return fig
