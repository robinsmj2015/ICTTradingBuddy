import pandas as pd

class Buffer:
    """
    Maintains a rolling buffer of tick-level data and trade-related annotations 
    for a given trading symbol. The buffer is updated in real time with incoming ticks, 
    strategy recommendations, and trade results. 

    Attributes:
        symbol (str): Ticker symbol for the instrument
        df (pd.DataFrame): Internal buffer storing ticks and trade metadata.
        buddy (object): Reference to the orchestrating Assistant or controller class.
    """

    def __init__(self, symbol: str, features: list):
        """
        Initializes the Buffer with a symbol and a list of feature columns to track.

        Args:
            symbol (str): The trading instrument symbol.
            features (list): List of feature column names expected in tick data.
        """
        self.symbol = symbol
        self.df = pd.DataFrame(columns=features + [
            "is_long", "confidence", "risk_reward", "entry", "stop_loss", "timeout", "take_profit",
            "num_contracts", "expected_revenue", "expected_profit",
            "actual_revenue", "actual_profit", "time_in_trade"
        ])
        self.df.index.name = "timestamp"
        self.buddy = None

    def write_features_to_buff(self, tick_data: dict) -> None:
        """
        Writes raw tick features into the buffer using the tick's timestamp as index.

        Args:
            tick_data (dict): Dictionary containing feature values and a "timestamp" key.
        """
        ts = tick_data["timestamp"]
        row_data = {col: tick_data.get(col, None) for col in self.df.columns}
        cleaned_data = {k: v for k, v in row_data.items() if k != "timestamp" and not pd.isna(v)}

        if cleaned_data:
            self.df.loc[ts] = cleaned_data

    def write_recs_to_buff(self, recs: dict) -> None:
        """
        Updates the buffer row corresponding to the current recommendation timestamp 
        with projected trade parameters (e.g., entry, SL, TP, confidence).

        Args:
            recs (dict): Dictionary of trade recommendation values.
        """
        ts = self.buddy.recommendation.timestamp
        if ts in self.df.index:
            for key, val in recs.items():
                if key in self.df.columns:
                    self.df.at[ts, key] = int(val) if isinstance(val, bool) else val

    def write_res_to_buff(self, ts: pd.Timestamp, actual_rev: float, actual_profit: float, time_in_trade: float) -> None:
        """
        Updates the buffer with realized trade results after trade exit.

        Args:
            ts (pd.Timestamp): Timestamp of the trade entry to update.
            actual_rev (float): Final revenue from the trade.
            actual_profit (float): Net profit/loss from the trade.
            time_in_trade (float): Duration of trade in seconds or minutes.
        """
        if ts in self.df.index:
            self.df.at[ts, "actual_revenue"] = actual_rev
            self.df.at[ts, "actual_profit"] = actual_profit
            self.df.at[ts, "time_in_trade"] = time_in_trade


