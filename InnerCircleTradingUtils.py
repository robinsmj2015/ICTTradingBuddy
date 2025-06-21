from typing import List, Tuple, Optional
from OrderBlocks import OrderBlocks
from LiquiditySweep import LiquiditySweep
from Fvg import Fvg
from SessionTimes import SessionTimes
import math
import pandas as pd


class InnerCircleTradingUtils:
    """
    A container for key Inner Circle Trading (ICT) utilities including:
    - Order block detection
    - Liquidity sweep identification
    - Fair Value Gap (FVG) processing
    - Session timing logic
    - ATR (Average True Range) calculation
    
    This class serves as a central hub to access modular ICT-based components.
    """

    def __init__(self):
        """
        Initializes all component utilities used in ICT-based signal analysis.
        """
        self.order_blocks = OrderBlocks()
        self.liq_sweep = LiquiditySweep()
        self.fvg = Fvg()
        self.session_times = SessionTimes()
    
    
    # -------------------------------------------------- ATR --------------------------------------------------------------------------

    @staticmethod
    def get_atr(df: pd.DataFrame) -> float:
        """
        Computes a 5-period Average True Range (ATR) from the input candle DataFrame.

        ATR is a measure of volatility that takes into account the greatest of:
        - High - Low
        - High - Previous Close
        - Low - Previous Close

        Args:
            df (pd.DataFrame): DataFrame containing at least 'high', 'low', and 'close' columns.

        Returns:
            float: The latest ATR value (rounded to 1 decimal). Defaults to 10 if data is insufficient.
        """
        # Shift close to get previous candle's close
        df["previous_close"] = df["close"].shift(1)

        # Calculate true range (TR) per row
        df["tr"] = df[["high", "low", "previous_close"]].apply(
            lambda row: max(
                row["high"] - row["low"],
                abs(row["high"] - row["previous_close"]),
                abs(row["low"] - row["previous_close"])
            ),
            axis=1
        )

        # Compute 5-period ATR from true range
        atr_series = df["tr"].rolling(window=5).mean()

        # Use most recent ATR value if available, otherwise fallback to 10
        atr_val = atr_series.iloc[-1] if not atr_series.isna().all() else 10

        return round(atr_val, 1)


    
    # ---------------------------------------------- Order Blocks --------------------------------------------------------------------------

    def detect_order_blocks(self, df, lookback=20):
        """
        Identifies unviolated bullish and bearish order blocks in a candle DataFrame.
        Expects columns: 'open', 'high', 'low', 'close'.

        Returns a list of dictionaries:
        {
            'timestamp': ..., 
            'type': 'bullish' or 'bearish',
            'index': ..., 
            'high': ..., 
            'low': ...
        }
        """
        return self.order_blocks._detect_order_blocks_(df, lookback)
    
    def score_order_blocks(self, price: float, order_blocks: List[dict]) -> int:
        """
        Score based on number of bullish/bearish OBs price is currently interacting with.
        """

        return self.order_blocks._score_order_blocks_(price, order_blocks)

    
    def get_nearest_ob_range(self, order_blocks, last_price, direction):

        return self.order_blocks._get_nearest_ob_range_(order_blocks, last_price, direction)
        
    
# ---------------------------------------------- FVG --------------------------------------------------------------------------
    
    def get_fvg_targets(self, df, direction, max_lookback=20):
        """
        Returns a list of FVG levels in the given trade direction.
        - 'long': looks for bullish FVGs above current price
        - 'short': looks for bearish FVGs below current price

        Each FVG is represented by a tuple: (fvg_low, fvg_high)
        """
        

        return self.fvg._get_fvg_targets_(df, direction, max_lookback)
    
    def score_fvg(self, price: float, fvg_zones: List[Tuple[float, float]], direction: str) -> int:
        """
        Score based on how many directional FVGs price is currently inside.
        """
        return self.fvg._score_fvg_(price, fvg_zones, direction)

# ---------------------------------------------- Liq sweep --------------------------------------------------------------------------

    
    def get_liquidity_pools(self, df, direction, tolerance=0.25, lookback=30, group_size=2):
        """
        Identifies liquidity pools (clusters of equal highs/lows) from recent candles.
        
        Args:
            df: DataFrame with 'high' and 'low' columns.
            direction: 'long' for sell-side (equal lows), 'short' for buy-side (equal highs).
            tolerance: Max difference to consider prices "equal".
            lookback: Number of recent candles to scan.
            group_size: Minimum number of similar highs/lows to qualify as a pool.

        Returns:
            Sorted list of price levels (floats) representing liquidity pools.
        """
        return self.liq_sweep._get_liquidity_pools(df, direction, tolerance, lookback, group_size)
    

    def score_liquidity_sweep(self, df, direction, pools, tolerance=0.25, lookback=25, group_size=2):
        """
        Sweep up = short bias, sweep down = long bias.
        `strength` indicates number of levels taken out.
        """
        return self.liq_sweep._score_liquidity_sweep_(df, direction, pools, tolerance, lookback, group_size)

# ----------------------------------------------Scalping Session ---------------------------------------------------------------------

    def ict_scalping_confidence(self, ts_str) -> str:
        """ confidence based on time of day trading periods"""
        
        return self.session_times._ict_scalping_confidence_(ts_str)

    
    def get_scalping_session_code(self, ts_str: str) -> str:
        """
        Classifies EDT timestamp into scalping windows:
        'ny_kill', 'reversal', or 'other'.
        
        Example input: '2025-05-01T09:35:03.123-04:00'
        """
        
        return self.session_times._get_scalping_session_code_(ts_str)
        

# -------------------------------------------- Pressure and fv dislocation scoring -------------------------------------------------

    @staticmethod
    def score_pressure_bias(pressure) -> int:
        """
        Score based on pressure imbalance (from volume delta or similar).
        """
        
        return max(-10, min(10, pressure))


    @staticmethod
    def score_fv_dislocation(fv_delta, scale=0.4) -> int:
        """
        Score dislocation between price and fair value using ICT principles.

        Positive delta → price above fair value (bearish bias → negative score)  
        Negative delta → price below fair value (bullish bias → positive score)

        Returns integer between -10 and +10.
        """
        
        if fv_delta is None:
            return 0
        # Assume delta is measured in points; scale using a factor
        normalized = -10 * math.tanh(scale * fv_delta)
        return round(normalized)

