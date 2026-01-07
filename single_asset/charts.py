
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


def plot_strategy_normalized(data: pd.DataFrame, result: pd.DataFrame, 
                            ticker: str, strategy_name: str,
                            colors: dict = None, display_mode: str = "base100"):
    """
    Graphique normalisé : Prix vs Stratégie avec double axe Y.
    """
    if colors is None:
        colors = {
            "blue": "#00d4ff",
            "green": "#00ff88",
            "card": "#1a1a1a",
            "text": "#ffffff",
            "orange": "#ffa500"
        }
    
    # Créer subplot avec secondary_y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if display_mode == "base100":
        # Base 100 normalisé
        price_norm = (data['Close'] / data['Close'].iloc[0]) * 100
        portfolio_norm = (result['portfolio_value'] / result['portfolio_value'].iloc[0]) * 100
        
        fig.add_trace(
            go.Scatter(x=data.index, y=price_norm,
                      name=f"Prix {ticker}",
                      line=dict(color=colors["orange"], width=2.5)),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=result.index, y=portfolio_norm,
                      name=f"Stratégie {strategy_name}",
                      line=dict(color=colors["green"], width=2.5)),
            secondary_y=True
        )
        
        fig.update_yaxes(title_text="Prix Asset (base 100)", secondary_y=False)
        fig.update_yaxes(title_text="Portfolio (base 100)", secondary_y=True)
        
    else:  # mode "returns"
        # Prix brut vs Portfolio value
        fig.add_trace(
            go.Scatter(x=data.index, y=data['Close'],
                      name=f"Prix {ticker} (EUR)",
                      line=dict(color=colors["orange"], width=2.5)),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=result.index, y=result['portfolio_value'],
                      name=f"Portfolio {strategy_name} (EUR)",
                      line=dict(color=colors["green"], width=2.5)),
            secondary_y=True
        )
        
        fig.update_yaxes(title_text=f"Prix {ticker} (€)", secondary_y=False)
        fig.update_yaxes(title_text="Valeur Portfolio (€)", secondary_y=True)
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=colors["card"],
        plot_bgcolor=colors["card"],
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(title="Date", color=colors["text"])
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


def plot_compare_strategies(results: dict, initial_capital: float = 10000, 
                           normalize: bool = True):
    """
    Compare plusieurs stratégies sur un même graphique.
    
    Args:
        results: dict avec {nom_stratégie: DataFrame}
        initial_capital: capital de départ
        normalize: si True, normalise toutes les courbes à base 100
    """
    fig = go.Figure()
    
    colors = ['#00d4ff', '#00ff88', '#ff6b6b', '#ffd93d', '#9d4edd', '#ff9f1c']
    
    for i, (name, data) in enumerate(results.items()):
        if normalize:
            # Normalisation à base 100
            values = (data['portfolio_value'] / data['portfolio_value'].iloc[0]) * 100
            yaxis_title = "Performance (Base 100)"
        else:
            values = data['portfolio_value']
            yaxis_title = "Valeur Portefeuille (€)"
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=values,
            mode='lines',
            name=name,
            line=dict(color=colors[i % len(colors)], width=2)
        ))
    
    # Ligne de référence
    reference_value = 100 if normalize else initial_capital
    fig.add_hline(
        y=reference_value, 
        line_dash="dash", 
        line_color="white", 
        opacity=0.5,
        annotation_text=f"Référence ({reference_value})"
    )
    
    fig.update_layout(
        title="Comparaison des Stratégies",
        xaxis_title="Date",
        yaxis_title=yaxis_title,
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