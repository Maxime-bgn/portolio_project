"""
Quant B - Portfolio Analysis Module
Multi-asset portfolio: simulation, metrics, visualization
"""

import pandas as pd
import numpy as np

DEFAULT_ASSETS = ["AAPL", "MSFT", "GOOGL", "XLF", "GLD"]


def calculate_returns(prices):
    """Calcule les rendements journaliers."""
    return prices.pct_change().dropna()


def create_equal_weights(assets):
    """Cree des poids egaux pour tous les assets."""
    n = len(assets)
    return {asset: 1.0 / n for asset in assets}


def normalize_weights(weights):
    """Normalise les poids pour qu'ils somment a 1."""
    total = sum(weights.values())
    if total == 0:
        return weights
    return {asset: w / total for asset, w in weights.items()}


def portfolio_value(prices, weights):
    """Calcule la valeur du portfolio dans le temps (base 100)."""
    normalized = (prices / prices.iloc[0]) * 100
    value = pd.Series(0.0, index=normalized.index)
    for asset, weight in weights.items():
        if asset in normalized.columns:
            value += normalized[asset] * weight
    return value


def volatility(returns, annualize=True):
    """Calcule la volatilite."""
    vol = returns.std()
    if annualize:
        vol *= np.sqrt(252)
    return vol * 100


def annual_return(returns):
    """Calcule le rendement annualise."""
    return returns.mean() * 252 * 100


def sharpe_ratio(returns, risk_free_rate=0.02):
    """Calcule le ratio de Sharpe."""
    ret = annual_return(returns) / 100
    vol = volatility(returns) / 100
    if vol == 0:
        return 0
    return (ret - risk_free_rate) / vol


def sortino_ratio(returns, risk_free_rate=0.02):
    """Calcule le ratio de Sortino (penalise seulement les baisses)."""
    ret = annual_return(returns) / 100
    downside = returns[returns < 0]
    if len(downside) == 0:
        return 0
    downside_std = downside.std() * np.sqrt(252)
    if downside_std == 0:
        return 0
    return (ret - risk_free_rate) / downside_std


def max_drawdown(prices):
    """Calcule la perte maximale."""
    rolling_max = prices.expanding().max()
    drawdown = (prices - rolling_max) / rolling_max
    return drawdown.min() * 100


def value_at_risk(returns, confidence=0.95):
    """Calcule la Value at Risk."""
    return np.percentile(returns, (1 - confidence) * 100) * 100


def diversification_ratio(returns, weights):
    """Calcule le ratio de diversification."""
    weighted_vols = 0
    for asset, weight in weights.items():
        if asset in returns.columns:
            vol = returns[asset].std() * np.sqrt(252)
            weighted_vols += weight * vol
    
    port_returns = pd.Series(0.0, index=returns.index)
    for asset, weight in weights.items():
        if asset in returns.columns:
            port_returns += returns[asset] * weight
    port_vol = port_returns.std() * np.sqrt(252)
    
    if port_vol == 0:
        return 1.0
    return weighted_vols / port_vol


def correlation_matrix(prices):
    """Matrice de correlation entre les assets."""
    returns = calculate_returns(prices)
    return returns.corr()


def analyze_portfolio(prices, weights):
    """Analyse complete du portfolio."""
    weights = normalize_weights(weights)
    returns = calculate_returns(prices)
    
    portfolio_returns = pd.Series(0.0, index=returns.index)
    for asset, weight in weights.items():
        if asset in returns.columns:
            portfolio_returns += returns[asset] * weight
    
    port_value = portfolio_value(prices, weights)
    
    metrics = {
        "annual_return": round(annual_return(portfolio_returns), 2),
        "volatility": round(volatility(portfolio_returns), 2),
        "sharpe_ratio": round(sharpe_ratio(portfolio_returns), 2),
        "sortino_ratio": round(sortino_ratio(portfolio_returns), 2),
        "max_drawdown": round(max_drawdown(port_value), 2),
        "var_95": round(value_at_risk(portfolio_returns, 0.95), 2),
        "diversification_ratio": round(diversification_ratio(returns, weights), 2)
    }
    
    asset_metrics = {}
    for asset in prices.columns:
        asset_ret = returns[asset]
        asset_prices = prices[asset]
        asset_metrics[asset] = {
            "return": round(annual_return(asset_ret), 2),
            "volatility": round(volatility(asset_ret), 2),
            "sharpe": round(sharpe_ratio(asset_ret), 2),
            "weight": round(weights.get(asset, 0) * 100, 1)
        }
    
    return {
        "portfolio": metrics,
        "assets": asset_metrics,
        "correlation": correlation_matrix(prices),
        "portfolio_value": port_value
    }
