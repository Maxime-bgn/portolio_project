"""
Advanced Analytics Module
Hurst exponent, multi-scale variance, regime detection
Based on ESILV Market Risk course 2024-2025
"""

import pandas as pd
import numpy as np
from scipy import stats


def estimate_hurst_exponent(returns):
    """
    Estimate Hurst exponent using course formula.
    
    Based on ESILV Market Risk course:
    Var(tau) = sigma^2 * tau^(2H)
    
    Estimator: H = (1/2) * log2(M'2 / M2)
    where M2 is variance at resolution N, M'2 at resolution N/2
    
    H = 0.5: random walk (Brownian motion)
    H > 0.5: persistent (trending, positive autocorrelation)
    H < 0.5: anti-persistent (mean-reverting, negative autocorrelation)
    
    Args:
        returns: Series of returns
        
    Returns:
        H: Hurst exponent
    """
    N = len(returns)
    
    if N < 4:
        return 0.5
    
    # M2: variance of increments at full resolution
    # Sum of squared increments
    M2 = np.sum(returns**2)
    
    # M'2: variance at half resolution
    # Aggregate returns by pairs
    half_res_returns = []
    for i in range(0, N-1, 2):
        if i+1 < N:
            half_res_returns.append(returns.iloc[i] + returns.iloc[i+1])
    
    if len(half_res_returns) < 2:
        return 0.5
    
    half_res_returns = np.array(half_res_returns)
    M2_prime = np.sum(half_res_returns**2)
    
    # Course formula: H = (1/2) * log2(M'2 / M2)
    if M2 > 0 and M2_prime > 0:
        H = 0.5 * np.log2(M2_prime / M2)
    else:
        H = 0.5
    
    # Constrain to valid range [0, 1]
    H = np.clip(H, 0, 1)
    
    return H


def multi_scale_variance(returns, scales=None):
    """
    Calculate variance at multiple time scales.
    
    Based on ESILV course: Var(tau) = sigma^2 * tau^(2H)
    For H=0.5 (random walk): Var(tau) = sigma^2 * tau
    
    Course also mentions: volatility annualization factor is tau^H (not sqrt(tau))
    
    Args:
        returns: Series of returns
        scales: List of time scales (in days)
        
    Returns:
        DataFrame with scales and corresponding variances
    """
    if scales is None:
        scales = [1, 5, 10, 20, 60]
    
    results = []
    
    # Variance at scale 1 (daily)
    var_1 = returns.var()
    
    for scale in scales:
        if scale >= len(returns):
            continue
            
        # Non-overlapping aggregated returns (as per course)
        aggregated = []
        for i in range(0, len(returns) - scale + 1, scale):
            if i + scale <= len(returns):
                agg_return = returns.iloc[i:i+scale].sum()
                aggregated.append(agg_return)
        
        if len(aggregated) > 1:
            variance = np.var(aggregated, ddof=1)
            
            # Ratio Var(tau) / Var(1)
            var_ratio = variance / var_1 if var_1 > 0 else 0
            
            # Theoretical ratio for random walk: tau
            # Actual ratio shows deviation from random walk
            
            results.append({
                'scale': scale,
                'variance': variance,
                'var_ratio': var_ratio,
                'theoretical_ratio': scale,  # For H=0.5
                'deviation': var_ratio / scale if scale > 0 else 0
            })
    
    return pd.DataFrame(results)


def detect_regimes_simple(prices, window=60):
    """
    Simple regime detection based on rolling statistics.
    
    Regimes:
    - Bull: positive trend + low volatility
    - Bear: negative trend + low volatility  
    - High Vol: high volatility regardless of trend
    - Sideways: low trend + low volatility
    
    Args:
        prices: Series of prices
        window: Rolling window for statistics
        
    Returns:
        Series of regime labels
    """
    returns = prices.pct_change().dropna()
    
    # Rolling statistics
    rolling_mean = returns.rolling(window).mean()
    rolling_std = returns.rolling(window).std()
    
    # Thresholds
    trend_threshold = 0.0005  # 0.05% per day
    vol_threshold = rolling_std.median()
    
    regimes = []
    
    for i in range(len(rolling_mean)):
        if pd.isna(rolling_mean.iloc[i]) or pd.isna(rolling_std.iloc[i]):
            regimes.append('Unknown')
            continue
            
        mean = rolling_mean.iloc[i]
        std = rolling_std.iloc[i]
        
        if std > vol_threshold * 1.5:
            regime = 'High Vol'
        elif mean > trend_threshold:
            regime = 'Bull'
        elif mean < -trend_threshold:
            regime = 'Bear'
        else:
            regime = 'Sideways'
        
        regimes.append(regime)
    
    return pd.Series(regimes, index=rolling_mean.index)


def variance_ratio_test(returns, lags=None):
    """
    Variance ratio test (Lo-MacKinlay).
    Tests if returns follow random walk.
    
    From course: VR(q) should equal 1 under random walk hypothesis
    VR(q) > 1: positive autocorrelation (momentum)
    VR(q) < 1: negative autocorrelation (mean reversion)
    
    Args:
        returns: Series of returns
        lags: List of lag periods to test
        
    Returns:
        DataFrame with variance ratios and test statistics
    """
    if lags is None:
        lags = [2, 5, 10, 20]
    
    results = []
    
    # Base variance (1-period)
    var_1 = returns.var()
    n = len(returns)
    
    for q in lags:
        if q >= n:
            continue
        
        # q-period returns
        q_returns = []
        for i in range(0, n - q, q):
            q_ret = returns.iloc[i:i+q].sum()
            q_returns.append(q_ret)
        
        if len(q_returns) < 2:
            continue
            
        var_q = np.var(q_returns)
        
        # Variance ratio
        vr = var_q / (q * var_1) if var_1 > 0 else 1
        
        # Test statistic (simplified)
        # Under random walk: VR should be 1
        # Standard error approximation
        se = np.sqrt((2 * (q - 1)) / (3 * q * n))
        z_stat = (vr - 1) / se if se > 0 else 0
        
        interpretation = 'Random Walk'
        if vr > 1.2:
            interpretation = 'Momentum'
        elif vr < 0.8:
            interpretation = 'Mean Reversion'
        
        results.append({
            'lag': q,
            'variance_ratio': vr,
            'z_statistic': z_stat,
            'interpretation': interpretation
        })
    
    return pd.DataFrame(results)


def fractional_differencing_check(returns):
    """
    Check if returns need fractional differencing.
    Based on Hurst exponent.
    
    Returns:
        dict with H and recommendation
    """
    H = estimate_hurst_exponent(returns)
    
    if H > 0.55:
        recommendation = "Series shows persistence. Consider fractional differencing with d < 1"
    elif H < 0.45:
        recommendation = "Series shows anti-persistence. Already stationary"
    else:
        recommendation = "Series close to random walk. Standard differencing OK"
    
    return {
        'hurst': H,
        'recommendation': recommendation
    }
