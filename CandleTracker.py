import pandas as pd
from ComputeIndicators import compute_indicators


class CandleTracker:
    """
    Tracks live tick data and aggregates it into fixed-duration candles.
    Computes technical indicators on finalized candles and stores results in a DataFrame.
    
    Attributes:
        duration (int): Candle duration in minutes.
        offset (int): Optional offset (in seconds) to shift candle start time.
        df (pd.DataFrame): Stores completed candle data with indicators.
        buddy (object): Reference to external object holding symbol and data_gather_time.
        _current (dict): Holds current open candle data.
        _last_volume (float): Stores last known tick volume for calculating volume delta.
    """

    def __init__(self, duration: int, offset: int = 0):
        """
        Initializes a CandleTracker instance.

        Args:
            duration (int): Candle duration in minutes.
            offset (int, optional): Optional offset in seconds to shift candle boundaries. Defaults to 0.
        """
        self.buddy = None
        self.duration = duration
        self.offset = offset
        self.df = pd.DataFrame(columns=[
            "symbol", "duration", "time_start", "time_end",
            "open", "close", "high", "low", "volume",
            "rsi_14", "stoch_rsi", "momentum_9",
            "ema_9", "ema_20", "sma_9", "sma_20",
            "vwma_20", "VWAP"
        ])
        self.df.index.name = "timestamp_start"
        self._current = None
        self._last_volume = None

    def add_tick(self, tick: dict) -> None:
        """
        Processes a new tick and updates the current candle.
        If a new candle period starts, finalizes the current one and computes indicators.

        Args:
            tick (dict): A dictionary containing at least 'timestamp', 'last', and 'volume' keys.
        """
        tick_time = pd.to_datetime(tick["timestamp"])
        tick_price = tick["last"]
        tick_volume = tick["volume"]

        # Calculate volume delta
        if self._last_volume is None:
            volume_delta = 0
        else:
            volume_delta = max(tick_volume - self._last_volume, 0)
        self._last_volume = tick_volume

        # Determine current candle window
        offset_td = pd.Timedelta(seconds=self.offset)
        candle_start = tick_time.floor(f"{self.duration}min") + offset_td
        candle_end = candle_start + pd.Timedelta(minutes=self.duration)

        # If new candle is required, finalize current and start a new one
        if self._current is None or self._current["time_start"] != candle_start:
            if self._current is not None:
                self.df.loc[self._current["time_start"]] = self._current
                self.df.index = pd.to_datetime(self.df.index)
                self.df = compute_indicators(self.df, self.buddy.data_gather_time)
            self._current = {
                "symbol": self.buddy.symbol,
                "duration": self.duration,
                "time_start": candle_start,
                "time_end": candle_end,
                "open": tick_price,
                "close": tick_price,
                "high": tick_price,
                "low": tick_price,
                "volume": volume_delta,
                "rsi_14": None, "stoch_rsi": None, "momentum_9": None,
                "ema_9": None, "ema_20": None, "sma_9": None, "sma_20": None,
                "vwma_20": None, "VWAP": None
            }
        else:
            self._current["close"] = tick_price
            self._current["high"] = (
                tick_price if self._current["high"] is None
                else self._current["high"] if tick_price is None
                else max(self._current["high"], tick_price)
            )
            self._current["low"] = (
                tick_price if self._current["low"] is None
                else self._current["low"] if tick_price is None
                else min(self._current["low"], tick_price)
            )
            self._current["volume"] += volume_delta
            self.add_indicators(self.buddy.data_gather_time)

    def add_indicators(self, data_gather_time: pd.Timestamp) -> None:
        """
        Computes technical indicators on the current candle DataFrame and updates it.

        Args:
            data_gather_time (pd.Timestamp): Reference time used for indicator calculation.
        """
        indicators_df = compute_indicators(self.df, data_gather_time)
        indicators_df = indicators_df.reindex(self.df.index)
        self.df.update(indicators_df)

