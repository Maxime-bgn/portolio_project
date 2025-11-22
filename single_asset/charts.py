"""
Graphiques de performance - Plotly
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def plot_price(data: pd.DataFrame):
    """Graphique du prix de l'actif."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name='Prix SG',
        line=dict(color='#00d4ff', width=2)
    ))
    fig.update_layout(
        title="Prix Société Générale (GLE.PA)",
        xaxis_title="Date",
        yaxis_title="Prix (€)",
        template="plotly_dark"
    )
    return fig


def plot_strategy(data: pd.DataFrame, strategy_name: str = "Stratégie"):
    """Graphique prix + valeur du portefeuille."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Prix SG", f"Portefeuille - {strategy_name}")
    )
    
    # Prix
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'],
        mode='lines', name='Prix',
        line=dict(color='#00d4ff', width=2)
    ), row=1, col=1)
    
    # Valeur portefeuille
    fig.add_trace(go.Scatter(
        x=data.index, y=data['portfolio_value'],
        mode='lines', name='Portefeuille',
        line=dict(color='#00ff88', width=2)
    ), row=2, col=1)
    
    fig.update_layout(
        height=600,
        template="plotly_dark",
        showlegend=True
    )
    return fig


def plot_compare_strategies(results: dict, initial_capital: float = 10000):
    """
    Compare plusieurs stratégies sur un même graphique.
    
    Args:
        results: dict avec {nom_stratégie: DataFrame}
    """
    fig = go.Figure()
    
    colors = ['#00d4ff', '#00ff88', '#ff6b6b', '#ffd93d']
    
    for i, (name, data) in enumerate(results.items()):
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['portfolio_value'],
            mode='lines',
            name=name,
            line=dict(color=colors[i % len(colors)], width=2)
        ))
    
    # Ligne capital initial
    fig.add_hline(y=initial_capital, line_dash="dash", line_color="white", opacity=0.5)
    
    fig.update_layout(
        title="Comparaison des Stratégies",
        xaxis_title="Date",
        yaxis_title="Valeur Portefeuille (€)",
        template="plotly_dark",
        hovermode="x unified"
    )
    return fig


def plot_drawdown(data: pd.DataFrame):
    """Graphique du drawdown."""
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
    """Histogramme des rendements journaliers."""
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=data['returns'].dropna() * 100,
        nbinsx=50,
        name='Rendements',
        marker_color='#00d4ff'
    ))
    
    fig.update_layout(
        title="Distribution des Rendements Journaliers",
        xaxis_title="Rendement (%)",
        yaxis_title="Fréquence",
        template="plotly_dark"
    )
    return fig