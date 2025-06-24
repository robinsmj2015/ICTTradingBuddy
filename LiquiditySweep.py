import pandas as pd
from typing import List


class LiquiditySweep:
    """
    Identifies and scores liquidity pool sweeps from recent price action.

    A liquidity sweep occurs when price aggressively moves through areas with 
    clustered liquidity (e.g., prior lows/highs), often signaling a trap or reversal zone.
    """

    def __init__(self):
        """
        Initializes the LiquiditySweep class.
        All functionality is provided through static methods.
        """
        pass

    @staticmethod
    def _get_liquidity_pools(
        df: pd.DataFrame,
        direction: str,
        tolerance: float,
        lookback: int,
        group_size: int
        ) -> List[float]:
        """
        Detects clustered price levels that act as liquidity pools using grouping logic.

        Args:
            df (pd.DataFrame): DataFrame with at least 'low', 'high', and 'close' columns.
            direction (str): 'long' to detect sell-side liquidity below; 'short' for buy-side above.
            tolerance (float): Allowed price variance to consider levels similar (e.g., 0.25).
            lookback (int): Number of past candles to examine.
            group_size (int): Minimum number of candles needed near a level to qualify as a pool.

        Returns:
            List[float]: Sorted liquidity pool levels based on proximity and direction.
        """
        lookback = min(lookback, len(df))
        prices = df.tail(lookback).copy()

        levels = prices["low"] if direction == "long" else prices["high"]
        pools = []

        visited = set()
        levels = levels.round(2)  # Round to reduce noise from tick-level fluctuations

        for _, price in levels.items():
            if price in visited:
                continue

            # Find similar prices within the tolerance
            similar = levels[(levels - price).abs() <= tolerance]
            if len(similar) >= group_size:
                avg_price = similar.mean()
                pools.append(avg_price)
                visited.update(similar)

        # Sort pools based on direction: below for long entries, above for short
        last_price = df.iloc[-1]["close"]
        if direction == "long":
            return sorted([p for p in pools if p < last_price], reverse=True)
        else:
            return sorted([p for p in pools if p > last_price])

    @staticmethod
    def _score_liquidity_sweep_(
        df: pd.DataFrame,
        direction: str,
        pools: List[float],
        tolerance: float = 0.25,
        lookback: int = 25,
        group_size: int = 2
        ) -> int:
        """
        Scores the presence of liquidity sweeps by comparing recent price movement across known pools.

        Args:
            df (pd.DataFrame): DataFrame with at least 'close' column.
            direction (str): 'long' for detecting sell-side sweeps, 'short' for buy-side.
            pools (List[float]): List of liquidity pool levels.
            tolerance (float): Not used in scoring but kept for interface consistency.
            lookback (int): Not used here but kept for consistency.
            group_size (int): Not used here but kept for interface consistency.

        Returns:
            int: Sweep score between -10 (long sweep) and +10 (short sweep).
        """
        if not pools:
            return 0

        last_price = df.iloc[-1]["close"]
        prior_price = df.iloc[-2]["close"] if len(df) > 1 else last_price

        swept = 0
        for level in pools:
            if direction == "long" and prior_price > level and last_price < level:
                swept += 1
            elif direction == "short" and prior_price < level and last_price > level:
                swept += 1

        # +3 per sweep, clamped to ±10, polarity depends on direction
        return min(10, swept * 3) if direction == "short" else max(-10, -swept * 3)
