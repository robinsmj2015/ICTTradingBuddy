from datetime import datetime, timedelta


class Trader:
    """
    Handles trade execution logic for entering and exiting trades based on confidence signals and market prices.

    Attributes:
        symbol (str): Trading symbol (e.g., "MNQ").
        entry_ratio_threshold (float): Confidence threshold to trigger a trade entry.
        lookback (int): Number of recent ticks to use for confidence averaging.
        balance (float): Current simulated trading balance.
        starting_balance (float): Initial balance for tracking performance.
        in_trade (bool): Flag indicating if currently in an active trade.
        trade_entry_time (datetime): Timestamp when the trade was entered.
        entry_price (float): Price at which the current trade was entered.
        sl (float): Stop-loss price.
        tp (float): Take-profit price.
        timeout (int): Maximum time allowed in trade (in seconds).
        position (str): Direction of trade, either "long" or "short".
        buddy (object): External object (must be set) providing access to tick data, candles, and buffers.
    """

    def __init__(self, symbol, entry_ratio_threshold=2, lookback=10, starting_balance=10000):
        self.symbol = symbol
        self.entry_ratio_threshold = entry_ratio_threshold
        self.lookback = lookback
        self.balance = starting_balance
        self.starting_balance = starting_balance
        self.in_trade = False
        self.trade_entry_time = None
        self.entry_price = None
        self.sl = None
        self.tp = None
        self.timeout = None
        self.position = None  # 'long' or 'short'
        self.buddy = None  # must be assigned externally

    def check_trading(self, data_gather_time):
        """
        Evaluate whether to enter or exit a trade based on current tick data and confidence signals.

        Entry:
            - Only enters a trade if not already in one.
            - Uses recent confidence scores to decide if the average absolute value exceeds threshold.
            - Assigns entry price, SL, TP, timeout, and direction based on last signal.

        Exit:
            - Trade is closed if one of the following is met:
                - Timeout is exceeded.
                - Take-profit is hit.
                - Stop-loss is triggered.
            - Profit or loss is calculated and logged to buffer.

        Args:
            data_gather_time (int): Minimum number of candles required before evaluating trades.
        """
        if len(self.buddy.candles[1].trackers[0].df) < data_gather_time:
            return

        tick = self.buddy.last_tick
        df = self.buddy.buff.df.tail(self.lookback)

        # Entry logic
        if not self.in_trade and df["confidence"] is not None:
            confidence_series = df["confidence"].dropna()
            if not confidence_series.empty:
                if confidence_series.abs().mean() > self.entry_ratio_threshold:
                    last = float(tick["last"])
                    latest = self.buddy.buff.df.iloc[-1]

                    self.in_trade = True
                    self.trade_entry_time = datetime.strptime(tick["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
                    self.entry_price = last
                    self.sl = latest["stop_loss"]
                    self.tp = latest["take_profit"]
                    self.timeout = latest["timeout"]
                    self.position = "long" if latest["confidence"] > 0 else "short"

        # Exit logic
        else:
            now = datetime.strptime(tick["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
            current_price = float(tick["last"])
            elapsed = (now - self.trade_entry_time).total_seconds()

            exit_trade = False
            

            if elapsed >= self.timeout:
                exit_trade = True
            elif self.position == "long" and current_price >= self.tp:
                exit_trade = True
            elif self.position == "long" and current_price <= self.sl:
                exit_trade = True
            elif self.position == "short" and current_price <= self.tp:
                exit_trade = True
            elif self.position == "short" and current_price >= self.sl:
                exit_trade = True

            if exit_trade:
                rev = self.buddy.points_to_dollars * (
                    (current_price - self.entry_price) if self.position == "long"
                    else (self.entry_price - current_price)
                )
                profit = rev - self.buddy.FEE_PER_CONTRACT_2_WAYS
                self.balance += profit
                self.in_trade = False

                entry_ts_str = self.trade_entry_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
                self.buddy.buff.write_res_to_buff(
                    ts=entry_ts_str,
                    actual_rev=rev,
                    actual_profit=profit,
                    time_in_trade=round(elapsed, 2)
                )
