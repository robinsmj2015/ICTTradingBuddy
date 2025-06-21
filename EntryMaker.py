class EntryMaker:
    """
    Generates an entry price for a trade using multiple contextual factors including:
    - Fair Value Gaps (FVGs)
    - Order Blocks (OBs)
    - VWAP alignment
    - Tick values like 'mark' and 'last'
    - ATR-based offset limits

    The logic aggregates valid sources and computes an average candidate entry, capped by ATR constraints.
    """

    def __init__(self):
        """
        Initializes the EntryMaker class.
        No internal state is maintained; all methods are static.
        """
        pass

    @staticmethod
    def _get_entry_price_(
        last_close: float,
        tick: dict,
        direction: str,
        fvg_zones: list,
        order_blocks: list,
        atr: float,
        vwap: float
    ) -> float:
        """
        Computes an entry price using a blend of key support/resistance signals and price alignment.

        Args:
            last_close (float): Most recent candle close price.
            tick (dict): Latest tick data with 'mark' and 'last' prices.
            direction (str): 'long' or 'short' indicating trade direction.
            fvg_zones (list): List of FVG zones (each as a (low, high) tuple).
            order_blocks (list): List of order block dictionaries with 'low' and 'high' keys.
            atr (float): Average True Range for constraining entry price range.
            vwap (float): VWAP value for current timeframe.

        Returns:
            float: Rounded entry price, based on blend of available references and ATR max offset.
        """
        if direction is None:
            return

        mark = tick["mark"]
        last = tick["last"]
        ob_entry = None
        fvg_entry = None
        vwap_entry = None

        trade_sign = 1 if direction == "long" else -1

        # Identify order block that surrounds last close
        ob = None
        for zone in order_blocks:
            if zone["low"] < last_close < zone["high"]:
                ob = zone
                break

        # Use OB edge adjusted by 0.25 if present
        if ob:
            ob_entry = ob["low"] + 0.25 if direction == "long" else ob["high"] - 0.25

        # Use FVG level as entry if current price is beyond FVG edge
        if fvg_zones:
            fvg = fvg_zones[0]
            if direction == "long" and fvg[0] < last_close:
                fvg_entry = fvg[0] + 0.25
            elif direction == "short" and fvg[1] > last_close:
                fvg_entry = fvg[1] - 0.25

        # Use VWAP as entry if favorable in direction
        if vwap:
            if direction == "long" and last and vwap < last:
                vwap_entry = vwap
            elif direction == "short" and last and vwap > last:
                vwap_entry = vwap

        # Average all available inputs
        summation = 0
        count = 0
        for val in [mark, last, ob_entry, fvg_entry, vwap_entry]:
            if val is not None:
                summation += val
                count += 1

        if not count:
            return last_close  # Fallback to last_close if no components are available

        proposed_entry = summation / count
        max_offset = 0.5 * atr  # Max allowable deviation from mark

        # Accept if within allowable range from mark
        if abs(proposed_entry - mark) <= max_offset:
            return round(4 * proposed_entry) / 4
        else:
            # Clip to max_offset from mark in trade direction
            return round(4 * (trade_sign * max_offset + mark)) / 4
