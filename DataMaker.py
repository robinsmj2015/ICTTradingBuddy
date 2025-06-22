
import random
from datetime import datetime

def make_synthetic_data(last_tick):
    """
    Simulates tick data, ±0.01% to mimic live price movement.

    Args: 
    last_tick (dict): last tick data

    """

    if not last_tick:
        last_tick["last"] = 1000.00
        last_tick["ask"] = 1000.00
        last_tick["bid"] = 1000.00
        last_tick["volume"] = 1000

        last_tick["bid_size"] = 1
        last_tick["ask_size"] = 1
        last_tick["last_size"] = 1

        last_tick["open"] = 1000.00
        last_tick["close"] = last_tick["last"]
        last_tick["high"] = max(last_tick["open"], last_tick["close"], last_tick["last"])
        last_tick["low"] = min(last_tick["open"], last_tick["close"], last_tick["last"])

    last_tick["last"] += random.uniform(-.01, .01) * last_tick["last"]
    last_tick["ask"] += random.uniform(0, .01) * last_tick["last"]
    last_tick["bid"] += random.uniform(-.01, 0) * last_tick["last"]
    
    for key in ["bid_size", "ask_size", "last_size"]:
        last_tick[key] = int(random.uniform(1, 5))

    last_tick["volume"] += int(random.uniform(10, 100)) 
    last_tick["mark"] = round((last_tick["bid"] + last_tick["ask"]) / 2, 2)
    last_tick["open"] = 1000.00
    last_tick["close"] = last_tick["last"]
    last_tick["high"] = max(last_tick["open"], last_tick["close"], last_tick["last"])
    last_tick["low"] = min(last_tick["open"], last_tick["close"], last_tick["last"])
    last_tick["net_change"] = round(last_tick["close"] - last_tick["open"], 2)
    last_tick["net_percent_change"] = round((last_tick["net_change"] / last_tick["open"]) * 100, 2)
    last_tick["fair_value_delta"] = round(last_tick["mark"] - last_tick["last"], 2)
    last_tick["zero_or_five"] = (int(last_tick["last"]) == last_tick["last"]) and (str(last_tick["last"])[-1] in ["0", "5"])
    last_tick["pressure"] = int(last_tick["bid_size"] - last_tick["ask_size"])
    last_tick["momentum"] = last_tick["last"] - last_tick["open"]
    last_tick["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    last_tick["symbol"] = "test"

    return last_tick
