import pandas as pd
from typing import List, Optional, Tuple, Union

class StopLoss:
    """
    Provides methods to calculate stop-loss levels for long or short trades
    using structure, order blocks, liquidity pools, FVG zones, and ATR.
    """

    def __init__(self):
        pass

    def _get_stop_loss_(
        self,
        df: pd.DataFrame,
        entry_price: float,
        direction: str,
        ob_range: Optional[Tuple[float, float]],
        fvg_zones: Optional[List[Tuple[float, float]]],
        atr: Optional[float],
        liq_pools: Optional[List[dict]]
    ) -> float:
        """
        Computes the stop loss price based on structure and other zone logic.

        Args:
            df (pd.DataFrame): DataFrame containing price data with 'low' and 'high' columns.
            entry_price (float): The price at which the trade was entered.
            direction (str): 'long' or 'short'.
            ob_range (Optional[Tuple[float, float]]): Order block as (high, low).
            fvg_zones (Optional[List[Tuple[float, float]]]): List of FVG zones [(low, high), ...].
            atr (Optional[float]): Average True Range value for fallback SL and bounding.
            liq_pools (Optional[List[dict]]): List of liquidity pools, each with at least a "high" key.

        Returns:
            float: Final stop loss price.
        """
        structure = df["low"].rolling(5).min().iloc[-1] if direction == "long" else df["high"].rolling(5).max().iloc[-1]
        structure_sl = structure - 0.25 if direction == "long" else structure + 0.25

        sl = self._stop_loss_helper_(entry_price, direction, ob_range, liq_pools, fvg_zones, atr)

        return min(structure_sl, sl) if direction == "long" else max(structure_sl, sl)

    def _stop_loss_helper_(
        self,
        entry_price: float,
        direction: str,
        ob_range: Optional[Tuple[float, float]] = None,
        liquidity_pools: Optional[List[dict]] = None,
        fvg_zones: Optional[List[Tuple[float, float]]] = None,
        atr: Optional[float] = None
    ) -> float:
        """
        Determines stop loss based on various components:
        order block, liquidity pools, FVG zones, and ATR.

        Args:
            entry_price (float): Entry price of the trade.
            direction (str): 'long' or 'short'.
            ob_range (Optional[Tuple[float, float]]): Order block as (high, low).
            liquidity_pools (Optional[List[dict]]): Liquidity zones with "high" or "low" keys.
            fvg_zones (Optional[List[Tuple[float, float]]]): FVG zones as (low, high) tuples.
            atr (Optional[float]): Average True Range for fallback SL and bounding.

        Returns:
            float: Computed stop loss level rounded to nearest 0.25.
        """
        sl = None

        if ob_range:
            ob_low, ob_high = ob_range[1], ob_range[0]
            sl = ob_low - 0.25 if direction == "long" else ob_high + 0.25

        if liquidity_pools:
            
            relevant = [
                p if isinstance(p, float) else p["high"]
                for p in liquidity_pools
                if (p["high"] < entry_price if direction == "long" else p["high"] > entry_price)]
            
            if relevant:
                liq_sl = min(relevant) - 0.25 if direction == "long" else max(relevant) + 0.25
                if sl is None or (liq_sl < sl if direction == "long" else liq_sl > sl):
                    sl = liq_sl

        if sl is None and fvg_zones:
            fvg = fvg_zones[0]
            sl = fvg[0] - 0.25 if direction == "long" else fvg[1] + 0.25

        if atr:
            fallback = entry_price - 0.5 * atr if direction == "long" else entry_price + 0.5 * atr
            if sl is None:
                sl = fallback
            else:
                sl = min(sl, fallback) if direction == "long" else max(sl, fallback)

            max_offset = 2 * atr
            sl = min(sl, entry_price - max_offset) if direction == "long" else max(sl, entry_price + max_offset)

        return round(4 * sl) / 4


















# class StopLoss:
#     def __init__(self):
#         pass

#     def _get_stop_loss_(self, df, entry_price, direction, ob_range, fvg_zones, atr, liq_pools):
       
#         structure = df["low"].rolling(5).min().iloc[-1] if direction == "long" else df["high"].rolling(5).max().iloc[-1]
#         structure_sl = structure - 0.25 if direction == "long" else structure + 0.25

#         sl = self._stop_loss_helper_(entry_price, direction, ob_range, liq_pools, fvg_zones, atr)

#         return min(structure_sl, sl) if direction == "long" else max(structure_sl, sl)

#     def _stop_loss_helper_(self, entry_price, direction, ob_range=None, liquidity_pools=None, fvg_zones=None, atr=None):
#         sl = None
#         if ob_range:
#             ob_low, ob_high = ob_range[1], ob_range[0]
#             sl = ob_low - 0.25 if direction == "long" else ob_high + 0.25

#         if liquidity_pools:
#             relevant = [p["high"] for p in liquidity_pools if (p["high"] < entry_price if direction == "long" else p > entry_price["low"])]
#             if relevant:
#                 liq_sl = min(relevant) - 0.25 if direction == "long" else max(relevant) + 0.25
#                 sl = liq_sl if sl is None or (liq_sl < sl if direction == "long" else liq_sl > sl) else sl

#         if sl is None and fvg_zones:
#             fvg = fvg_zones[0]
#             sl = fvg[0] - 0.25 if direction == "long" else fvg[1] + 0.25

#         if atr:
#             fallback = entry_price - 0.5 * atr if direction == "long" else entry_price + 0.5 * atr
#             sl = fallback if sl is None else min(sl, fallback) if direction == "long" else max(sl, fallback)

#         max_offset = 2 * atr

#         sl = min(sl, entry_price - max_offset) if direction == "long" else max(sl, entry_price + max_offset)

#         return round(4 * sl) / 4