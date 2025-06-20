from typing import List, Optional, Tuple, Union

class TakeProfit:
    """
    Provides logic for computing a take-profit level based on multiple technical 
    trading zones and constraints. It integrates order block ranges, fair value gaps 
    (FVGs), liquidity pools, average true range (ATR), and VWAP to determine 
    optimal take-profit prices for both long and short trades.
    """

    def __init__(self):
        """
        Initializes the TakeProfit class.
        Currently acts as a placeholder since all logic is implemented in static methods.
        """
        pass

    @staticmethod
    def _get_take_profit_(
        entry_price: float,
        direction: str,
        ob_range: Optional[Tuple[float, float]],
        fvg_targets: List[Tuple[float, float]],
        liq_pools: List[dict],
        atr: float,
        vwap: Optional[float]
    ) -> float:
        """
        Calculates a take-profit level using a combination of order block distance, 
        fair value gap targets, liquidity pool targets, VWAP, and ATR-based bounding.

        Args:
            entry_price (float): The price at which the trade was entered.
            direction (str): 'long' or 'short' indicating trade direction.
            ob_range (Optional[Tuple[float, float]]): Order block high/low range.
            fvg_targets (List[Tuple[float, float]]): Fair value gap zones as (low, high).
            liq_pools (List[dict]): Liquidity zones with 'high' or 'low' levels.
            atr (float): Average True Range used for fallback targets and maximum bounds.
            vwap (Optional[float]): VWAP price used to further cap the target if available.

        Returns:
            float: Calculated take-profit price, rounded to the nearest 0.25.
        """

        # Use distance to far end of order block if available, else default
        r = abs(entry_price - ob_range[1 if direction == "long" else 0]) if ob_range else 5

        # Base take profit from 1.5x OB distance
        tp = entry_price + 1.5 * r if direction == "long" else entry_price - 1.5 * r

        # Adjust take profit using first matching FVG target
        for fvg in fvg_targets:
            if direction == "long" and fvg[0] > entry_price and fvg[0] < tp:
                tp = fvg[0]
                break
            if direction == "short" and fvg[1] < entry_price and fvg[1] > tp:
                tp = fvg[1]
                break

        # Adjust take profit using first matching liquidity pool level
        for pool in liq_pools:
            if direction == "long" and pool["high"] > entry_price and pool["high"] < tp:
                tp = pool["high"] - 0.25
                break
            if direction == "short" and pool["low"] < entry_price and pool["low"] > tp:
                tp = pool["low"] + 0.25
                break

        # Use VWAP to further restrict the TP level
        if vwap:
            tp = min(tp, vwap) if direction == "long" else max(tp, vwap)

        # Fallback: if TP ends up on the wrong side of entry, apply 3x ATR
        if direction == "long" and tp < entry_price:
            tp = entry_price + 3 * atr
        elif direction == "short" and tp > entry_price:
            tp = entry_price - 3 * atr

        # Hard cap: no more than 4x ATR move
        max_move = 4 * atr
        tp = min(tp, entry_price + max_move) if direction == "long" else max(tp, entry_price - max_move)

        # Round to nearest 0.25
        return round(4 * tp) / 4
