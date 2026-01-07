"""
Métriques de performance - Société Générale
"""
import pandas as pd
import numpy as np


def total_return(data: pd.DataFrame) -> float:
    """Rendement total en %."""
    start = data["portfolio_value"].dropna().iloc[0]
    end = data["portfolio_value"].dropna().iloc[-1]
    return ((end - start) / start) * 100


def annualized_return(data: pd.DataFrame, trading_days: int = 252) -> float:
    """Rendement annualisé en %."""
    total_ret = total_return(data) / 100
    nb_days = len(data)
    years = nb_days / trading_days
    return ((1 + total_ret) ** (1 / years) - 1) * 100


def volatility(data: pd.DataFrame, trading_days: int = 252) -> float:
    """Volatilité annualisée en %."""
    return data["returns"].std() * np.sqrt(trading_days) * 100


def sharpe_ratio(data: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
    """Ratio de Sharpe : rendement ajusté au risque."""
    ann_ret = annualized_return(data) / 100
    vol = volatility(data) / 100
    if vol == 0:
        return 0
    return (ann_ret - risk_free_rate) / vol


def max_drawdown(data: pd.DataFrame) -> float:
    """Max Drawdown : perte maximale depuis un pic en %."""
    values = data["portfolio_value"].dropna()
    peak = values.expanding().max()
    drawdown = (values - peak) / peak
    return drawdown.min() * 100


def win_rate(data: pd.DataFrame) -> float:
    """Pourcentage de jours gagnants."""
    returns = data["returns"].dropna()
    return (returns > 0).sum() / len(returns) * 100


def profit_factor(data: pd.DataFrame) -> float:
    """Ratio gains / pertes."""
    returns = data["returns"].dropna()
    gains = returns[returns > 0].sum()
    losses = abs(returns[returns < 0].sum())
    if losses == 0:
        return float("inf")
    return gains / losses


def calmar_ratio(data: pd.DataFrame) -> float:
    """Ratio Calmar : rendement / max drawdown."""
    mdd = abs(max_drawdown(data))
    if mdd == 0:
        return 0
    return annualized_return(data) / mdd


def get_all_metrics(data: pd.DataFrame) -> dict:
    """Retourne toutes les métriques."""
    return {
        "Total Return (%)": round(total_return(data), 2),
        "Annualized Return (%)": round(annualized_return(data), 2),
        "Volatility (%)": round(volatility(data), 2),
        "Sharpe Ratio": round(sharpe_ratio(data), 2),
        "Max Drawdown (%)": round(max_drawdown(data), 2),
        "Win Rate (%)": round(win_rate(data), 2),
        "Profit Factor": round(profit_factor(data), 2),
        "Calmar Ratio": round(calmar_ratio(data), 2)
    }
