import pandas as pd
import numpy as np

def calc_simple_moving_average(df: pd.DataFrame, n: int, col: str, create=True) -> pd.Series:
    if create:
        df[f"{col}_sma_{n}"] = df[col].rolling(n).mean()
        return None
    else:
        return df[col].rolling(n).mean()

def calc_exponential_moving_average(df: pd.DataFrame, n: int, col: str, adjust: bool=False, create=True) -> pd.Series:
    if create:
        df[f"{col}_ema_{n}"] = df[col].ewm(n, adjust=adjust).mean()
        return None
    else:
        return df[col].ewm(n, adjust=adjust).mean()

def calc_weight_moving_average(df: pd.DataFrame, n: int, col: str, create=True) -> pd.Series:
    weights = list(range(1, n+1))
    if create:
        df[f"{col}_wma_{n}"] = df[col].rolling(n).apply(lambda x: np.average(x, weights=weights))
        return None
    else:
        return df[col].rolling(n).apply(lambda x: np.average(x, weights=weights))

def calc_macd(df: pd.DataFrame, col: str):
    df[f"{col}_macd"] = df[f"{col}_ema_12"] - df[f"{col}_ema_26"]
    df[f"{col}_macd_signal"] = calc_exponential_moving_average(df, 9, f"{col}_macd", create=False)
    df[f"{col}_macd_osc"] = df[f"{col}_macd"] - df[f"{col}_macd_signal"]

def calc_envelop(df: pd.DataFrame, rate: int, col:str):
    rate_percent = rate / 100
    df[f"{col}_rate_{rate}"] = rate_percent * df[col]

def calc_itimoku(df: pd.DataFrame):
    df["high_26"] = df["high"].rolling(26).max()
    df["low_26"] = df["low"].rolling(26).min()
    df["basic_line"] = (df["high_26"] + df["low_26"])/2

    df["high_9"] = df["high"].rolling(9).max()
    df["low_9"] = df["low"].rolling(9).min()
    df["change_line"] = (df["high_9"] + df["low_9"])/2

    df["forward_span1"] = ((df["basic_line"] + df["change_line"]) / 2).shift(26)

    df["high_52"] = df["high"].rolling(52).max()
    df["low_52"] = df["low"].rolling(52).min()
    df["forward_span2"] = ((df["high_52"] + df["low_52"])/2).shift(26)

    df["backward_span"] = df["close"].shift(-26)

def calc_bollingger_bands(df: pd.DataFrame, n: int, col: str,  sigma: int):
    df[f"{col}_std_{n}"] = df[col].rolling(n).std()
    df[f"{col}_plus_{sigma}_sigma"] = df[col] + sigma * df[f"{col}_std_{n}"]
    df[f"{col}_minas_{sigma}_sigma"] = df[col] - sigma * df[f"{col}_std_{n}"]
    df[f"{col}_minas_{sigma}_sigma"] = df[f"{col}_minas_{sigma}_sigma"].apply(lambda x: x if x > 0 else 0)

def calc_parabolic(df: pd.DataFrame):
    sar= []
    ep = None
    af = 0.02
    trend = True
    chenge_trend = False

    for i, high, low, close in enumerate(df["high"], df["low"], df["close"]):
        if len(sar) == 0:
            sar.append(low)
        else:
            sar.append(sar[i-1] + af * (ep - sar[i-1]))
        
        if ep is None:
            ep = high
        elif chenge_trend:
            chenge_trend = False
            if trend:
                ep = high
            else:
                ep = low
        elif trend:
            if high > ep:
                ep = high
        else:
            if low < ep:
                ep = low
