import requests
from datetime import datetime
import streamlit as st
import time
import random


def get_last_tick(symbol="bitcoin"):
    try:
        price_data = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        ).json()

        market_data = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol}"
        ).json()

        # Optional OHLC if needed (1-minute candles, limited to 1 day)
        ohlc_data = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol}/ohlc?vs_currency=usd&days=1"
        ).json()

    except Exception as e:
        st.error(f"Failed to fetch CoinGecko data: {e}")
        return {}

    st.write(price_data)
    st.write(market_data)
    st.write(ohlc_data[:2])  # Show first couple of OHLC entries

    time.sleep(30)

    market = market_data.get("market_data", {})
    current_price = market.get("current_price", {}).get("usd", 0.0)
    open_price = market.get("ath", {}).get("usd", current_price)  # fallback
    volume = market.get("total_volume", {}).get("usd", 0.0)
    high = market.get("high_24h", {}).get("usd", current_price)
    low = market.get("low_24h", {}).get("usd", current_price)

    last_tick = {
        "last": float(current_price),
        "ask":  random.uniform(0, .01) * float(current_price), #"NOT AVAILABLE",
        "bid":  random.uniform(-.01, 0) * float(current_price), #"NOT AVAILABLE",
        "volume": float(volume),
        "bid_size": int(random.uniform(1, 5)), #"NOT AVAILABLE",
        "ask_size": int(random.uniform(1, 5)), #"NOT AVAILABLE",
        "last_size": int(random.uniform(1, 5)), #"NOT AVAILABLE",
        "open": float(open_price),
        "close": float(current_price),
        "high": float(high),
        "low": float(low),
        "mark": random.uniform(-.01, .01) * float(current_price), #"NOT AVAILABLE",
        "symbol": symbol.upper(),
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    }

    try:
        last_tick["net_change"] = round(last_tick["close"] - last_tick["open"], 2)
        last_tick["net_percent_change"] = round((last_tick["net_change"] / last_tick["open"]) * 100, 2)
        last_tick["fair_value_delta"] = round(last_tick["mark"] - last_tick["last"], 2)
        last_tick["zero_or_five"] = (int(last_tick["last"]) == last_tick["last"]) and (str(int(last_tick["last"]))[-1] in ["0", "5"])
        last_tick["pressure"] = last_tick["bid_size"] - last_tick["ask_size"]
        last_tick["momentum"] = last_tick["last"] - last_tick["open"]
    except:
        pass

    return last_tick
