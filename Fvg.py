import pandas as pd
from typing import List, Tuple


class Fvg:
    """
    Detects Fair Value Gaps (FVGs) and computes signal strength scores based on 
    price interaction with those gaps.

    Fair Value Gaps are short-term imbalances in price action often followed 
    by mean reversion or continuation moves. This utility class identifies those gaps
    and scores their alignment with current price action.
    """

    def __init__(self):
        """
        Initializes the Fvg class.
        No internal state is stored; methods are static.
        """
        pass

    @staticmethod
    def _get_fvg_targets_(
        df: pd.DataFrame,
        direction: str,
        max_lookback: int
        ) -> List[Tuple[float, float]]:
        """
        Scans recent candles for bullish or bearish Fair Value Gaps (FVGs).

        Args:
            df (pd.DataFrame): DataFrame with at least 'high', 'low', and 'close' columns.
            direction (str): 'long' to detect bullish FVGs, 'short' for bearish.
            max_lookback (int): Number of recent candles to scan.

        Returns:
            List[Tuple[float, float]]: List of FVG zones (low, high), sorted by proximity to current price.
        """
        fvgs = []

        # Start from -i = 3 to avoid index underflow
        for i in range(2, min(len(df), max_lookback + 2)):
            prev = df.iloc[-(i + 1)]
            mid = df.iloc[-i]
            curr = df.iloc[-(i - 1)]

            # Bullish FVG (price gap to the upside)
            if prev["low"] > mid["high"] and curr["low"] > mid["high"]:
                fvg_low = mid["high"]
                fvg_high = min(prev["low"], curr["low"])
                if direction == "long":
                    fvgs.append((fvg_low, fvg_high))

            # Bearish FVG (price gap to the downside)
            if prev["high"] < mid["low"] and curr["high"] < mid["low"]:
                fvg_high = mid["low"]
                fvg_low = max(prev["high"], curr["high"])
                if direction == "short":
                    fvgs.append((fvg_low, fvg_high))

        # Sort FVGs by distance from last closing price
        last_close = df.iloc[-1]["close"]
        fvgs.sort(key=lambda zone: abs((zone[0] + zone[1]) / 2 - last_close))

        return fvgs

    @staticmethod
    def _score_fvg_(
        price: float,
        fvg_zones: List[Tuple[float, float]],
        direction: str
    ) -> int:
        """
        Scores whether the current price sits inside any known FVG zones.

        Args:
            price (float): The current or reference price.
            fvg_zones (List[Tuple[float, float]]): List of FVG (low, high) zones.
            direction (str): 'long' or 'short' trade direction.

        Returns:
            int: Score between -10 (strong short) and +10 (strong long), based on overlap.
        """
        score = 0
        for low, high in fvg_zones:
            if low <= price <= high:
                score += 2 if direction == "long" else -2

        # Clamp score to range [-10, 10] and reverse polarity for shorts
        return max(-10, min(10, score if direction == "short" else -score))
