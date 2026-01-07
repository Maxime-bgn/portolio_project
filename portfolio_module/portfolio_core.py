"""
Quant B 
"""

import pandas as pd
import numpy as np
from scipy import stats

DEFAULT_ASSETS = ["AAPL", "MSFT", "GOOGL", "XLF", "GLD"]

def calculate_returns(prices):
    return prices.pct_change().dropna()


def calculate_log_returns(prices):
    return np.log(prices / prices.shift(1)).dropna()

def create_equal_weights(assets):
    n = len(assets)
    return {asset: 1.0 / n for asset in assets}


def normalize_weights(weights):
    total = sum(weights.values())
    if total == 0:
        return {asset: 1.0 / len(weights) for asset in weights}
    return {asset: w / total for asset, w in weights.items()}


def portfolio_value(prices, weights, rebalancing_freq='never'):
    if rebalancing_freq == 'never':
        # Buy and hold simple
        normalized = (prices / prices.iloc[0]) * 100
        value = pd.Series(0.0, index=normalized.index)
        for asset, weight in weights.items():
            if asset in normalized.columns:
                value += normalized[asset] * weight
        return value
    returns = calculate_returns(prices)
    value = [100.0]
    current_weights = weights.copy()
    
    rebal_months = {'monthly': 1, 'quarterly': 3, 'yearly': 12}.get(rebalancing_freq, 999)
    last_rebal_month = prices.index[0].month
    
    for i in range(len(returns)):
        date = returns.index[i]
        if (date.month - last_rebal_month) % rebal_months == 0 and date.day <= 5:
            current_weights = weights.copy()
            last_rebal_month = date.month
        port_return = sum(returns.iloc[i][asset] * w 
                         for asset, w in current_weights.items() 
                         if asset in returns.columns)
        
        value.append(value[-1] * (1 + port_return))
        for asset in current_weights:
            if asset in returns.columns:
                current_weights[asset] *= (1 + returns.iloc[i][asset])
        total = sum(current_weights.values())
        if total > 0:
            current_weights = {k: v/total for k, v in current_weights.items()}
    
    return pd.Series(value[1:], index=returns.index)


def annual_return(returns):
    total_return = (1 + returns).prod() - 1
    n_years = len(returns) / 252
    if n_years == 0:
        return 0
    cagr = (1 + total_return) ** (1 / n_years) - 1
    return cagr * 100


def volatility(returns, annualize=True):
    vol = returns.std()
    if annualize:
        vol *= np.sqrt(252)
    return vol * 100


def sharpe_ratio(returns, risk_free_rate=0.02):
    ret = annual_return(returns) / 100
    vol = volatility(returns) / 100
    if vol == 0:
        return 0
    return (ret - risk_free_rate) / vol


def sortino_ratio(returns, risk_free_rate=0.02, target_return=0):
    ret = annual_return(returns) / 100
    downside_returns = returns[returns < target_return/252]
    if len(downside_returns) == 0:
        return float('inf') if ret > risk_free_rate else 0
    
    downside_std = downside_returns.std() * np.sqrt(252)
    if downside_std == 0:
        return float('inf') if ret > risk_free_rate else 0
    
    return (ret - risk_free_rate) / downside_std


def calmar_ratio(returns, prices):

    ret = annual_return(returns) / 100
    mdd = abs(max_drawdown(prices) / 100)
    if mdd == 0:
        return 0
    return ret / mdd


def max_drawdown(prices):
    rolling_max = prices.expanding().max()
    drawdown = (prices - rolling_max) / rolling_max
    return drawdown.min() * 100


def current_drawdown(prices):
    peak = prices.max()
    current = prices.iloc[-1]
    return ((current - peak) / peak) * 100


def value_at_risk(returns, confidence=0.95):

    var = np.percentile(returns, (1 - confidence) * 100)
    return var * 100


def conditional_var(returns, confidence=0.95):
    var_threshold = np.percentile(returns, (1 - confidence) * 100)
    tail_losses = returns[returns <= var_threshold]
    if len(tail_losses) == 0:
        return 0
    return tail_losses.mean() * 100


def information_ratio(returns, benchmark_returns):
    excess_returns = returns - benchmark_returns
    tracking_error = excess_returns.std() * np.sqrt(252)
    if tracking_error == 0:
        return 0
    active_return = excess_returns.mean() * 252
    return active_return / tracking_error


def beta(returns, market_returns):
    covariance = returns.cov(market_returns)
    market_variance = market_returns.var()
    if market_variance == 0:
        return 0
    return covariance / market_variance


def alpha(returns, market_returns, risk_free_rate=0.02):
    port_return = annual_return(returns) / 100
    port_beta = beta(returns, market_returns)
    market_return = annual_return(market_returns) / 100
    
    expected_return = risk_free_rate + port_beta * (market_return - risk_free_rate)
    return (port_return - expected_return) * 100


def treynor_ratio(returns, market_returns, risk_free_rate=0.02):
    ret = annual_return(returns) / 100
    port_beta = beta(returns, market_returns)
    if port_beta == 0:
        return 0
    return (ret - risk_free_rate) / port_beta


def win_rate(returns):
    if len(returns) == 0:
        return 0
    return (returns > 0).sum() / len(returns) * 100


def profit_factor(returns):
    gains = returns[returns > 0].sum()
    losses = abs(returns[returns < 0].sum())
    if losses == 0:
        return float('inf') if gains > 0 else 0
    return gains / losses


def skewness(returns):
    return returns.skew()


def kurtosis(returns):
    return returns.kurtosis()


def tail_ratio(returns):
    right_tail = np.percentile(returns, 95)
    left_tail = abs(np.percentile(returns, 5))
    if left_tail == 0:
        return 0
    return right_tail / left_tail


def diversification_ratio(returns, weights):
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


def effective_number_assets(weights, returns):
    # HHI based on weights
    hhi = sum(w**2 for w in weights.values())
    return 1 / hhi if hhi > 0 else 0


def rolling_sharpe(returns, window=60):
    rolling = returns.rolling(window=window)
    rolling_mean = rolling.mean() * 252
    rolling_std = rolling.std() * np.sqrt(252)
    return rolling_mean / rolling_std


def ulcer_index(prices):

    running_max = prices.expanding().max()
    drawdown_pct = ((prices - running_max) / running_max) * 100
    squared_drawdowns = drawdown_pct ** 2
    ulcer = np.sqrt(squared_drawdowns.mean())
    return ulcer


def recovery_factor(prices):
    total_return = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
    mdd = abs(max_drawdown(prices))
    if mdd == 0:
        return 0
    return total_return / mdd


def correlation_matrix(prices):
    returns = calculate_returns(prices)
    return returns.corr()

def analyze_portfolio(prices, weights, market_returns=None):
    weights = normalize_weights(weights)
    returns = calculate_returns(prices)
    
    # Portfolio returns
    portfolio_returns = pd.Series(0.0, index=returns.index)
    for asset, weight in weights.items():
        if asset in returns.columns:
            portfolio_returns += returns[asset] * weight
    
    # Portfolio value
    port_value = portfolio_value(prices, weights)
    metrics = {
        "annual_return": round(annual_return(portfolio_returns), 2),
        "volatility": round(volatility(portfolio_returns), 2),
        "downside_deviation": round(volatility(portfolio_returns[portfolio_returns < 0]), 2),
        "sharpe_ratio": round(sharpe_ratio(portfolio_returns), 2),
        "sortino_ratio": round(sortino_ratio(portfolio_returns), 2),
        "calmar_ratio": round(calmar_ratio(portfolio_returns, port_value), 2),
        "information_ratio": round(information_ratio(portfolio_returns, 
                                   market_returns if market_returns is not None 
                                   else portfolio_returns), 2),
        "max_drawdown": round(max_drawdown(port_value), 2),
        "current_drawdown": round(current_drawdown(port_value), 2),
        "ulcer_index": round(ulcer_index(port_value), 2),
        "recovery_factor": round(recovery_factor(port_value), 2),
        "var_95": round(value_at_risk(portfolio_returns, 0.95), 2),
        "cvar_95": round(conditional_var(portfolio_returns, 0.95), 2),
        "var_99": round(value_at_risk(portfolio_returns, 0.99), 2),
        "skewness": round(skewness(portfolio_returns), 2),
        "kurtosis": round(kurtosis(portfolio_returns), 2),
        "tail_ratio": round(tail_ratio(portfolio_returns), 2),
        "win_rate": round(win_rate(portfolio_returns), 2),
        "profit_factor": round(profit_factor(portfolio_returns), 2),
        "diversification_ratio": round(diversification_ratio(returns, weights), 2),
        "effective_n_assets": round(effective_number_assets(weights, returns), 2),
    }
    if market_returns is not None and len(market_returns) > 0:
        metrics["beta"] = round(beta(portfolio_returns, market_returns), 2)
        metrics["alpha"] = round(alpha(portfolio_returns, market_returns), 2)
        metrics["treynor_ratio"] = round(treynor_ratio(portfolio_returns, market_returns), 2)
    asset_metrics = {}
    for asset in prices.columns:
        asset_ret = returns[asset]
        asset_prices = prices[asset]
        asset_metrics[asset] = {
            "return": round(annual_return(asset_ret), 2),
            "volatility": round(volatility(asset_ret), 2),
            "sharpe": round(sharpe_ratio(asset_ret), 2),
            "sortino": round(sortino_ratio(asset_ret), 2),
            "max_dd": round(max_drawdown(asset_prices), 2),
            "var_95": round(value_at_risk(asset_ret, 0.95), 2),
            "weight": round(weights.get(asset, 0) * 100, 1)
        }
    
    return {
        "portfolio": metrics,
        "assets": asset_metrics,
        "correlation": correlation_matrix(prices),
        "portfolio_value": port_value,
        "returns_series": portfolio_returns
    }


def compare_portfolios(prices_list, weights_list, names):
    results = []
    
    for prices, weights, name in zip(prices_list, weights_list, names):
        analysis = analyze_portfolio(prices, weights)
        metrics = analysis["portfolio"]
        metrics["name"] = name
        results.append(metrics)
    
    df = pd.DataFrame(results)
    df = df.set_index("name")
    return df
