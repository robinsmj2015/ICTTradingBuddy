import pandas as pd
from CandleTracker import CandleTracker


class OffsetCandleManager:
    """
    Manages multiple CandleTracker instances with different offset start times 
    to capture nuanced candle formations across multiple intrabar variations.

    This approach is particularly useful for detecting patterns that might only appear 
    in shifted time slices (e.g., ICT-style offset candles).

    Attributes:
        duration (int): Candle duration in minutes.
        offsets (List[int]): List of offset values in seconds to shift candle start times.
        trackers (Dict[int, CandleTracker]): Mapping from offset to associated CandleTracker.
    """

    def __init__(self, duration: int, offsets=[0, 10, 20, 30, 40, 50]):
        """
        Initializes the OffsetCandleManager with multiple CandleTrackers.

        Args:
            duration (int): Duration of each candle in minutes.
            offsets (List[int]): List of offset values (in seconds) to shift candle starts.
        """
        self.duration = duration
        self.offsets = offsets
        self.trackers = {
            offset: CandleTracker(duration, offset=offset)
            for offset in offsets
        }

    def set_buddy(self, buddy) -> None:
        """
        Sets the shared context (`buddy`) for all internal CandleTrackers.

        Args:
            buddy (object): The shared orchestrator object containing symbol and state references.
        """
        for tracker in self.trackers.values():
            tracker.buddy = buddy

    def add_tick(self, tick: dict) -> None:
        """
        Adds a new tick to all tracked offset-based CandleTrackers.

        Args:
            tick (dict): A single tick containing at least 'timestamp', 'last', and 'volume'.
        """
        for tracker in self.trackers.values():
            tracker.add_tick(tick)

    def get_latest_candles(self) -> dict:
        """
        Retrieves the most recent in-progress candle for each offset.

        Returns:
            dict: A dictionary mapping offset to the latest candle dict from each tracker.
        """
        candles = {}
        for offset, tracker in self.trackers.items():
            if tracker._current:
                candles[offset] = tracker._current.copy()
        return candles

    def get_combined_df(self) -> pd.DataFrame:
        """
        Concatenates all CandleTracker DataFrames into a single DataFrame 
        with an added 'offset' column for debugging or downstream analysis.

        Returns:
            pd.DataFrame: Combined and sorted DataFrame of all candles across offsets.
        """
        all_dfs = []
        for offset, tracker in self.trackers.items():
            df = tracker.df.copy()
            df["offset"] = offset
            all_dfs.append(df)
        return pd.concat(all_dfs).sort_index()

