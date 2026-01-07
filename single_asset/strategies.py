# Backtesting strategies - Société Générale
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier


def macd_crossover(data: pd.DataFrame, initial_capital: float = 10000,
                   fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    # MACD crossover strategy: Buy when MACD crosses above signal line
    # MACD = EMA(fast) - EMA(slow)
    # Signal = EMA of MACD
    # Position = 1 when MACD > Signal, else 0
    df = data.copy()
    df["returns"] = df["Close"].pct_change()

    # Compute MACD components
    df["EMA_fast"] = df["Close"].ewm(span=fast, adjust=False).mean()
    df["EMA_slow"] = df["Close"].ewm(span=slow, adjust=False).mean()
    df["MACD"] = df["EMA_fast"] - df["EMA_slow"]
    df["MACD_signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()

    # Generate trading signals
    df["signal"] = (df["MACD"] > df["MACD_signal"]).astype(int)
    df["strategy_returns"] = df["signal"].shift(1) * df["returns"]

    # Compute equity curve
    df["cumulative_returns"] = (1 + df["strategy_returns"].fillna(0)).cumprod()
    df["portfolio_value"] = initial_capital * df["cumulative_returns"]
    df["strategy"] = "MACD Crossover"

    return df


def buy_and_hold(data: pd.DataFrame, initial_capital: float = 10000) -> pd.DataFrame:
    # Buy and hold strategy: Stay fully invested at all times
    df = data.copy()
    df["returns"] = df["Close"].pct_change()
    df["cumulative_returns"] = (1 + df["returns"]).cumprod()
    df["portfolio_value"] = initial_capital * df["cumulative_returns"]
    df["strategy"] = "Buy and Hold"
    return df


def end_of_month(data: pd.DataFrame, initial_capital: float = 10000) -> pd.DataFrame:
    # End-of-month strategy: Buy for the last 3 trading days of each month
    df = data.copy()
    df["returns"] = df["Close"].pct_change()
    df["day_of_month"] = df.index.day

    # Identify last 3 calendar days of each month
    df["is_month_end"] = df.groupby([df.index.year, df.index.month])["day_of_month"].transform(
        lambda x: x >= x.max() - 2
    )

    df["signal"] = df["is_month_end"].astype(int)
    df["strategy_returns"] = df["signal"].shift(1) * df["returns"]
    df["cumulative_returns"] = (1 + df["strategy_returns"].fillna(0)).cumprod()
    df["portfolio_value"] = initial_capital * df["cumulative_returns"]
    df["strategy"] = "End of Month"
    return df


def volatility_breakout(data: pd.DataFrame, initial_capital: float = 10000,
                        k: float = 0.5) -> pd.DataFrame:
    # Volatility breakout: Buy when price breaks above previous day's high + k * range
    df = data.copy()
    df["returns"] = df["Close"].pct_change()

    df["prev_range"] = (df["High"] - df["Low"]).shift(1)
    df["prev_high"] = df["High"].shift(1)
    df["breakout_level"] = df["prev_high"] + k * df["prev_range"]

    df["signal"] = (df["High"] > df["breakout_level"]).astype(int).shift(1).fillna(0)

    df["strategy_returns"] = df["signal"] * df["returns"]
    df["cumulative_returns"] = (1 + df["strategy_returns"].fillna(0)).cumprod()
    df["portfolio_value"] = initial_capital * df["cumulative_returns"]
    df["strategy"] = "Volatility Breakout"

    return df


def trend_following(data: pd.DataFrame, initial_capital: float = 10000,
                    ma_period: int = 50) -> pd.DataFrame:
    # Trend following: Buy if price > moving average
    df = data.copy()
    df["returns"] = df["Close"].pct_change()
    df["MA"] = df["Close"].rolling(window=ma_period).mean()

    df["signal"] = (df["Close"] > df["MA"]).astype(int)
    df["strategy_returns"] = df["signal"].shift(1) * df["returns"]
    df["cumulative_returns"] = (1 + df["strategy_returns"].fillna(0)).cumprod()
    df["portfolio_value"] = initial_capital * df["cumulative_returns"]
    df["strategy"] = "Trend Following"
    return df


def golden_cross(data: pd.DataFrame, initial_capital: float = 10000) -> pd.DataFrame:
    # Golden Cross: Buy when MA50 crosses above MA200 (long-term momentum)
    df = data.copy()
    df["returns"] = df["Close"].pct_change()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["MA200"] = df["Close"].rolling(window=200).mean()

    df["signal"] = (df["MA50"] > df["MA200"]).astype(int)
    df["strategy_returns"] = df["signal"].shift(1) * df["returns"]
    df["cumulative_returns"] = (1 + df["strategy_returns"].fillna(0)).cumprod()
    df["portfolio_value"] = initial_capital * df["cumulative_returns"]
    df["strategy"] = "Golden Cross"
    return df


def rsi_oversold(data: pd.DataFrame, initial_capital: float = 10000,
                 period: int = 14, oversold: int = 30) -> pd.DataFrame:
    # RSI Oversold: Buy when RSI < oversold threshold
    df = data.copy()
    df["returns"] = df["Close"].pct_change()

    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["signal"] = (df["RSI"] < oversold).astype(int)
    df["strategy_returns"] = df["signal"].shift(1) * df["returns"]
    df["cumulative_returns"] = (1 + df["strategy_returns"].fillna(0)).cumprod()
    df["portfolio_value"] = initial_capital * df["cumulative_returns"]
    df["strategy"] = "RSI Oversold"
    return df


def linear_regression_strategy(data: pd.DataFrame, initial_capital: float = 10000,
                               lookback: int = 20) -> pd.DataFrame:
    # Linear regression forecasting strategy:
    # Train model on last N days, predict tomorrow
    # Long if tomorrow > today
    df = data.copy()
    df["returns"] = df["Close"].pct_change()
    df["signal"] = 0
    df["predicted"] = np.nan

    prices = df["Close"].values

    for i in range(lookback, len(df)):
        X_train = np.arange(lookback).reshape(-1, 1)
        y_train = prices[i - lookback:i]

        model = LinearRegression()
        model.fit(X_train, y_train)

        X_pred = np.array([[lookback]])
        predicted_price = model.predict(X_pred)[0]

        df.iloc[i, df.columns.get_loc("predicted")] = predicted_price

        if predicted_price > prices[i]:
            df.iloc[i, df.columns.get_loc("signal")] = 1

    df["strategy_returns"] = df["signal"].shift(1) * df["returns"]
    df["cumulative_returns"] = (1 + df["strategy_returns"].fillna(0)).cumprod()
    df["portfolio_value"] = initial_capital * df["cumulative_returns"]
    df["strategy"] = "Linear Regression"

    return df
