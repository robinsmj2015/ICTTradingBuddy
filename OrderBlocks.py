import pandas as pd
from typing import List, Optional, Dict, Union, Tuple

class OrderBlocks:
    """
    A utility class for detecting and scoring bullish and bearish order blocks 
    from candlestick data. Order blocks represent institutional buying or selling zones, 
    identified by a shift in market structure and validated by future price behavior.

    Methods:
        _detect_order_blocks_: Identifies valid bullish or bearish order blocks in historical data.
        _score_order_blocks_: Scores the influence of order blocks near the current price.
        _get_nearest_ob_range_: Finds the nearest order block of a specified type relative to price.
    """

    def __init__(self):
        """
        Initializes the OrderBlocks class.
        All methods are static and can be called without instantiating.
        """
        pass

    @staticmethod
    def _detect_order_blocks_(df: pd.DataFrame, lookback: int = 20) -> List[Dict[str, Union[str, int, float, pd.Timestamp]]]:
        """
        Scans recent candles and identifies valid bullish or bearish order blocks 
        based on engulfing patterns and validation by subsequent price action.

        Args:
            df (pd.DataFrame): Candlestick data with 'open', 'high', 'low', 'close' columns.
            lookback (int): Number of candles to look back for order block formation.

        Returns:
            List[Dict]: A list of dictionaries, each representing a valid order block:
                {
                    'timestamp': pd.Timestamp of OB,
                    'type': 'bullish' or 'bearish',
                    'index': index in df where OB occurred,
                    'high': float value of OB high,
                    'low': float value of OB low
                }
        """
        order_blocks = []

        for i in range(1, min(len(df), lookback)):
            prev = df.iloc[-(i + 1)]
            curr = df.iloc[-i]
            ob_type = None

            # Bullish Order Block: Red → Green engulfing with breakout
            if prev["close"] < prev["open"] and curr["close"] > curr["open"] and curr["close"] > prev["high"]:
                ob_type = "bullish"
                ob_high = prev["high"]
                ob_low = prev["low"]

            # Bearish Order Block: Green → Red engulfing with breakdown
            elif prev["close"] > prev["open"] and curr["close"] < curr["open"] and curr["close"] < prev["low"]:
                ob_type = "bearish"
                ob_high = prev["high"]
                ob_low = prev["low"]

            if ob_type:
                ob_index = len(df) - i
                ob_candle_idx = df.index.get_loc(df.index[ob_index])
                violated = False

                # Ensure price has not invalidated the OB (i.e., closed beyond OB limits)
                for j in range(ob_candle_idx + 1, len(df)):
                    test_close = df.iloc[j]["close"]
                    if ob_type == "bullish" and test_close < ob_low:
                        violated = True
                        break
                    if ob_type == "bearish" and test_close > ob_high:
                        violated = True
                        break

                if not violated:
                    order_blocks.append({
                        "timestamp": prev.name,
                        "type": ob_type,
                        "index": ob_index,
                        "high": ob_high,
                        "low": ob_low
                    })

        return order_blocks

    @staticmethod
    def _score_order_blocks_(price: float, order_blocks: List[Dict]) -> int:
        """
        Scores the density of bullish or bearish order blocks near a given price level.

        Args:
            price (float): The current market price.
            order_blocks (List[Dict]): List of order block dictionaries (as returned by `_detect_order_blocks_`).

        Returns:
            int: A score between -10 (strong bullish zone) and +10 (strong bearish zone),
                 scaled by number of overlapping OBs.
        """
        bullish_hits = 0
        bearish_hits = 0

        for ob in order_blocks:
            if ob["low"] <= price <= ob["high"]:
                if ob["type"] == "bullish":
                    bullish_hits += 1
                elif ob["type"] == "bearish":
                    bearish_hits += 1

        net = bearish_hits - bullish_hits
        return max(-10, min(10, net * 3))  # 3 points per OB, capped between -10 and +10

    @staticmethod
    def _get_nearest_ob_range_(
        order_blocks: List[Dict[str, Union[str, float]]],
        last_price: float,
        direction: str
    ) -> Optional[Tuple[float, float]]:
        """
        Finds the (high, low) range of the nearest order block in the given direction.

        Args:
            order_blocks (List[Dict]): List of order block dictionaries.
            last_price (float): The current or last-traded price.
            direction (str): Type of OB to search for: 'bullish' or 'bearish'.

        Returns:
            Optional[Tuple[float, float]]: (high, low) of the nearest matching order block, 
                                           or None if no such block exists.
        """
        candidates = [
            ob for ob in order_blocks
            if 'type' in ob and ob["type"] == direction
        ]

        if not candidates:
            return None  # No OBs of that type

        # Sort by proximity to current price (midpoint of OB)
        candidates.sort(key=lambda ob: abs((ob["high"] + ob["low"]) / 2 - last_price))

        nearest = candidates[0]
        return (nearest["high"], nearest["low"])


















# class OrderBlocks:
#     def __init__(self):
#         pass
    
#     @staticmethod
#     def _detect_order_blocks_(df, lookback=20):
#         order_blocks = []

#         for i in range(1, min(len(df), lookback)):
#             prev = df.iloc[-(i + 1)]
#             curr = df.iloc[-i]
#             ob_type = None

#             # Bullish OB
#             if prev["close"] < prev["open"] and curr["close"] > curr["open"] and curr["close"] > prev["high"]:
#                 ob_type = "bullish"
#                 ob_high = prev["high"]
#                 ob_low = prev["low"]

#             # Bearish OB
#             elif prev["close"] > prev["open"] and curr["close"] < curr["open"] and curr["close"] < prev["low"]:
#                 ob_type = "bearish"
#                 ob_high = prev["high"]
#                 ob_low = prev["low"]

#             if ob_type:
#                 ob_index = len(df) - i
#                 ob_candle_idx = df.index.get_loc(df.index[ob_index])
#                 violated = False

#                 # Check if price closed beyond OB after it formed
#                 for j in range(ob_candle_idx + 1, len(df)):
#                     test_close = df.iloc[j]["close"]
#                     if ob_type == "bullish" and test_close < ob_low:
#                         violated = True
#                         break
#                     if ob_type == "bearish" and test_close > ob_high:
#                         violated = True
#                         break

#                 if not violated:
#                     order_blocks.append({
#                         "timestamp": prev.name,
#                         "type": ob_type,
#                         "index": ob_index,
#                         "high": ob_high,
#                         "low": ob_low
#                     })
    
#         return order_blocks
    
#     @staticmethod
#     def _score_order_blocks_(price, order_blocks):
#         bullish_hits = 0
#         bearish_hits = 0

#         for ob in order_blocks:
#             if ob["low"] <= price <= ob["high"]:
#                 if ob["type"] == "bullish":
#                     bullish_hits += 1
#                 elif ob["type"] == "bearish":
#                     bearish_hits += 1

#         net = bearish_hits - bullish_hits
#         return max(-10, min(10, net * 3))  # ~3 pts per block
    
#     @staticmethod
#     def _get_nearest_ob_range_(order_blocks, last_price, direction):
#         """
#         Returns (high, low) of the nearest OB in the given direction ('bullish' or 'bearish')
#         relative to current price.
#         """
        
#         #print(order_blocks)

       

#         candidates = [
#             ob for ob in order_blocks
#             if 'type' in ob and ob["type"] == direction
#         ]

#         if not candidates:
#             return None  # No OBs of that type

#         # Sort by distance to current price
#         candidates.sort(key=lambda ob: abs((ob["high"] + ob["low"]) / 2 - last_price))

#         nearest = candidates[0]
#         return (nearest["high"], nearest["low"])