"""
ComputeIndicators.py

This module contains utility functions to compute technical indicators on candle data
and to generate a numeric score summarizing indicator alignment for trading decisions.
It uses `pandas_ta` for computing standard indicators such as RSI, EMA, VWAP, etc.
"""

import pandas as pd
import pandas_ta as ta


def compute_indicators(df: pd.DataFrame, data_gather_time: int) -> pd.DataFrame:
    """
    Computes a set of technical indicators on the last 50 rows of a candle DataFrame.

    Args:
        df (pd.DataFrame): Candle DataFrame with 'close', 'high', 'low', and 'volume' columns.
        data_gather_time (int): Minimum required length of the DataFrame to compute indicators.

    Returns:
        pd.DataFrame: Modified DataFrame with the most recent row updated with computed indicators.
    """
    if len(df) < data_gather_time:
        return df

    # Work on a copy of the DataFrame
    #df = df.reset_index(drop=True).copy()
    df = df.copy()

    # Ensure datetime index is sorted
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # Use last 50 rows for calculation
    recent = df.tail(50).copy()

    if len(recent) > 9:
        recent['momentum_9'] = ta.mom(recent['close'], length=9)
        recent['ema_9'] = ta.ema(recent['close'], length=9)
        recent['sma_9'] = ta.sma(recent['close'], length=9)

        # VWAP
        vwap = ta.vwap(recent['high'], recent['low'], recent['close'], recent['volume'])
        if vwap is not None and not vwap.empty:
            if isinstance(vwap, pd.Series):
                vwap = vwap.to_frame(name='VWAP')
            vwap = vwap[~vwap.index.duplicated(keep='last')]
            recent = recent.drop(columns=[col for col in vwap.columns if col in recent.columns], errors='ignore')
            recent = recent.join(vwap)

        if len(recent) > 14:
            recent['rsi_14'] = ta.rsi(recent['close'], length=14)
            stoch_rsi = ta.stochrsi(recent['close'], length=14)
            recent['stoch_rsi'] = stoch_rsi.iloc[:, 0]

            if len(recent) > 20:
                recent['ema_20'] = ta.ema(recent['close'], length=20)
                recent['sma_20'] = ta.sma(recent['close'], length=20)
                recent['vwma_20'] = ta.vwma(recent['close'], recent['volume'], length=20)



    # Copy most recent indicator values to the last row of the original DataFrame
    last = recent.iloc[-1]
    for col in [
        'rsi_14', 'stoch_rsi', 'momentum_9',
        'ema_9', 'ema_20', 'sma_9', 'sma_20',
        'vwma_20', 'VWAP'
    ]:
        df.at[df.index[-1], col] = last.get(col, None)

    return df

def _get_inds_(candle: dict) -> tuple[int, dict]:
    """
    Computes a score based on technical indicators and pivot levels for a given candle,
    and returns a subindicator dictionary with bullish (1), bearish (-1), or neutral (0) signals.

    Args:
        candle (dict): Dictionary of indicator values from a candle row.

    Returns:
        tuple[int, dict]: A signal score between -10 and +10, and a dictionary of subindicator signals.
    """
    score = 0
    subindicators = {}

    # RSI
    rsi = candle.get("rsi_14", 50) or 50
    if rsi < 30:
        score += 2
        subindicators["rsi"] = 1
    elif rsi > 70:
        score -= 2
        subindicators["rsi"] = -1
    else:
        subindicators["rsi"] = 0

    # Stochastic RSI
    stoch = candle.get("stoch_rsi", 0.5) or 0.5
    if stoch < 0.2:
        score += 2
        subindicators["stoch_rsi"] = 1
    elif stoch > 0.8:
        score -= 2
        subindicators["stoch_rsi"] = -1
    else:
        subindicators["stoch_rsi"] = 0

    # Momentum
    momentum = candle.get("momentum_9", 0) or 0
    if momentum > 0:
        score += 2
        subindicators["momentum"] = 1
    elif momentum < 0:
        score -= 2
        subindicators["momentum"] = -1
    else:
        subindicators["momentum"] = 0


    # EMA crossover
    ema_fast = candle.get("ema_9")
    ema_slow = candle.get("ema_20")
    if ema_fast is not None and ema_slow is not None:
        if ema_fast > ema_slow:
            score += 2
            subindicators["ema_cross"] = 1
        elif ema_fast < ema_slow:
            score -= 2
            subindicators["ema_cross"] = -1
        else:
            subindicators["ema_cross"] = 0
    else:
        subindicators["ema_cross"] = 0

    # VWAP position
    close = candle.get("close")
    vwap = candle.get("VWAP")
    if close is not None and vwap is not None:
        if close > vwap:
            score += 2
            subindicators["vwap_position"] = 1
        elif close < vwap:
            score -= 2
            subindicators["vwap_position"] = -1
        else:
            subindicators["vwap_position"] = 0
    else:
        subindicators["vwap_position"] = 0

    return max(-10, min(10, round(score))), subindicators
