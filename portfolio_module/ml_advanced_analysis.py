import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from hmmlearn.hmm import GaussianHMM
from xgboost import XGBClassifier



# This part is linked to our machine learning project.
# It is also visible on the same github.

def create_features(df, weights):
    returns = df.pct_change().dropna()
    
    portfolio_returns = pd.Series(0.0, index=returns.index)
    for asset, weight in weights.items():
        if asset in returns.columns:
            portfolio_returns += returns[asset] * weight
    
    features = pd.DataFrame(index=portfolio_returns.index)
    features["Return"] = portfolio_returns
    features["Vol_21d"] = portfolio_returns.rolling(21).std() * np.sqrt(252)
    features["Vol_5d"] = portfolio_returns.rolling(5).std() * np.sqrt(252)
    
    return features.dropna(), portfolio_returns


def detect_regimes(features, n_states=3):
    scaler = StandardScaler()
    X = scaler.fit_transform(features)
    
    model = GaussianHMM(n_components=n_states, covariance_type="full", n_iter=100, random_state=42)
    model.fit(X)
    states = model.predict(X)
    
    stats = []
    names = ["Low Vol", "Normal", "High Vol"]
    for i in range(n_states):
        mask = states == i
        if mask.sum() > 0:
            ret_mean = features.loc[mask, "Return"].mean() * 252 * 100
            ret_std = features.loc[mask, "Return"].std() * np.sqrt(252) * 100
            regime_name = names[i] if i < 3 else "Regime " + str(i)
            stats.append({
                "Regime": regime_name,
                "Return (%)": str(round(ret_mean, 1)),
                "Vol (%)": str(round(ret_std, 1)),
                "Days": int(mask.sum())
            })
    
    return {"states": states, "stats": pd.DataFrame(stats)}


def predict_regimes(features, states):
    df = features.copy()
    df["target"] = pd.Series(states, index=features.index).shift(-5)
    df = df.dropna()
    
    split = int(len(df) * 0.8)
    X_train = df.iloc[:split].drop("target", axis=1).values
    y_train = df.iloc[:split]["target"].astype(int).values
    X_test = df.iloc[split:].drop("target", axis=1).values
    y_test = df.iloc[split:]["target"].astype(int).values
    
    model = XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    importance = pd.DataFrame({
        "Feature": df.drop("target", axis=1).columns,
        "Importance": model.feature_importances_
    }).sort_values("Importance", ascending=False)
    
    return {
        "predictions": y_pred,
        "actual": y_test,
        "dates": df.index[split:],
        "accuracy": (y_pred == y_test).mean(),
        "importance": importance
    }


def plot_regimes(portfolio_value, states, colors):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=portfolio_value.index, y=portfolio_value,
        mode="lines", name="Portfolio",
        line=dict(color="white", width=2)
    ))
    
    regime_colors = [colors["green"], colors["blue"], colors["red"]]
    for i in np.unique(states):
        mask = states == i
        if mask.sum() > 0:
            fig.add_trace(go.Scatter(
                x=portfolio_value.index[mask], y=portfolio_value.values[mask],
                mode="markers", name="Regime " + str(i),
                marker=dict(size=4, color=regime_colors[i % 3])
            ))
    
    fig.update_layout(
        title="HMM Regime Detection",
        template="plotly_dark",
        paper_bgcolor=colors["card"],
        plot_bgcolor=colors["card"],
        font=dict(color=colors["text"]),
        height=400
    )
    return fig


def plot_predictions(results, portfolio_value, colors):
    dates = results["dates"]
    pred = results["predictions"]
    portfolio_test = portfolio_value.loc[dates]
    
    fig = go.Figure()
    regime_colors = [colors["green"], colors["blue"], colors["red"]]
    
    for i in np.unique(pred):
        mask = pred == i
        fig.add_trace(go.Scatter(
            x=dates[mask], y=portfolio_test.values[mask],
            mode="markers", name="Predicted " + str(i),
            marker=dict(size=6, color=regime_colors[i % 3])
        ))
    
    acc_pct = round(results["accuracy"] * 100, 1)
    fig.update_layout(
        title="XGBoost Predictions (Acc: " + str(acc_pct) + "%)",
        template="plotly_dark",
        paper_bgcolor=colors["card"],
        plot_bgcolor=colors["card"],
        font=dict(color=colors["text"]),
        height=400
    )
    return fig


def plot_importance(importance, colors):
    top = importance.head(5)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top["Importance"], y=top["Feature"],
        orientation="h", marker_color=colors["accent"]
    ))
    
    fig.update_layout(
        title="Feature Importance",
        template="plotly_dark",
        paper_bgcolor=colors["card"],
        plot_bgcolor=colors["card"],
        font=dict(color=colors["text"]),
        height=300
    )
    return fig


def ml_advanced_analysis(df, weights, colors):
    try:
        features, portfolio_returns = create_features(df, weights)
        portfolio_value = (1 + portfolio_returns).cumprod() * 100
        
        hmm_results = detect_regimes(features)
        regime_fig = plot_regimes(portfolio_value.loc[features.index], hmm_results["states"], colors)
        
        xgb_results = predict_regimes(features, hmm_results["states"])
        pred_fig = plot_predictions(xgb_results, portfolio_value.loc[features.index], colors)
        importance_fig = plot_importance(xgb_results["importance"], colors)
        
        return {
            "hmm_fig": regime_fig,
            "xgb_fig": pred_fig,
            "importance_fig": importance_fig,
            "hmm_stats": hmm_results["stats"],
            "xgb_rmse": 1 - xgb_results["accuracy"]
        }
        
    except Exception as e:
        raise Exception("ML analysis failed: " + str(e))