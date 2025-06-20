"""
System Setup for Trading Buddy

This script initializes the trading environment by:
- Creating shared objects for each equity symbol (buddies)
- Registering and creating strategy instances
- Wiring together components like Trader, Strategy, Plotter, Buffer, Recommendation, Visualizer, and CandleTracker

"""

from Assistant import Assistant
from Buffer import Buffer
from CandleTracker import CandleTracker
from Strategy import Strategy
from StratICT import StratICT
from datetime import datetime, timedelta
from Plotter import Plotter
from Recommendation import Recommendation
from Trader import Trader
from OffsetCandleManager import OffsetCandleManager


# ------------------------- Core Parameters -----------------------------
equities = ["test"]  # which equity to track
data_gather_time = 2  # time to wait before displaying visuals and making recs
candle_durations = {1, 2, 3, 5, 15}  # candle duratons
to_use_plotter = False  # set True to enable Matplotlib animation


# ------------------------- Constants ----------------------------------
POINTS_TO_DOLLARS = {"test": 1}
FIELD_ROWS = {
    "last": 2, "bid": 3, "ask": 4, "bid_size": 5, "ask_size": 6,
    "mark": 7, "volume": 8, "high": 9, "low": 10, "open": 11,
    "close": 12, "net_change": 13, "net_percent_change": 14,
    "last_size": 15, "pressure": 16, "fair_value_delta": 17,
    "momentum": 18, "zero_or_five": 19
}

# ------------------------- Strategy -------------------------
strategy_factory = Strategy()

# ------------------------- Create Buddies -----------------------------
buddies = {}
for eq in equities:
    buffer = Buffer(eq, list(FIELD_ROWS.keys()))
    plotter = Plotter(eq)
    rec = Recommendation(eq)
    trader = Trader(eq)
    strategy_factory.register_strategy("strat_ict_" + eq, StratICT)
    strat = strategy_factory.create("strat_ict_" + eq)

    candles = {cd: CandleTracker(cd) for cd in candle_durations}
    candles[1] = OffsetCandleManager(duration=1)

    buddies[eq] = Assistant(
        data_gather_time, eq, POINTS_TO_DOLLARS[eq],
        trader, buffer, plotter, candles, strat, rec
    )

# ------------------------- Wire parent (buddy) instances to each class instance --------------------------
for b in buddies.values():
    b.strat.buddy = b
    b.recommendation.buddy = b
    b.buff.buddy = b
    b.plotter.buddy = b
    b.trader.buddy = b
    for candle in b.candles.values():
        if isinstance(candle, OffsetCandleManager):
            candle.set_buddy(b)
        else:
            candle.buddy = b

# ------------------------- Startup Message ----------------------------
future_time = (datetime.now() + timedelta(minutes=data_gather_time)).time()
print(f"Trading Buddy will be collecting data until {future_time.strftime('%H:%M')}")

