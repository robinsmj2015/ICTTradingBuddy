import requests
from datetime import datetime
import streamlit as st
import time


def get_last_tick(symbol="BTCUSDT"):
    ticker = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}").json()
    book = requests.get(f"https://api.binance.com/api/v3/ticker/bookTicker?symbol={symbol}").json()
    trade = requests.get(f"https://api.binance.com/api/v3/trades?symbol={symbol}&limit=1").json()
    data = requests.get(f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}").json()


    st.write(ticker)
    st.write(book)
    st.write(trade)
    st.write(data)

    time.sleep(30)
     
    last_tick = {
        "last": float(trade["price"]),
        "ask": float(book["askPrice"]),
        "bid": float(book["bidPrice"]),
        "volume": float(ticker["volume"]),
        "bid_size": float(book["bidQty"]),
        "ask_size": float(book["askQty"]),
        "last_size": float(trade["qty"]),
        "open": float(ticker["openPrice"]),
        "close": float(ticker["lastPrice"]),
        "high": float(ticker["highPrice"]),
        "low": float(ticker["lowPrice"]),
        "float": float(data["markPrice"]),
        "symbol": "BTC",
        "timestamp":  datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]}
    
    
    last_tick["net_change"] = round(last_tick["close"] - last_tick["open"], 2)
    last_tick["net_percent_change"] = round((last_tick["net_change"] / last_tick["open"]) * 100, 2)
    last_tick["fair_value_delta"] = round(last_tick["mark"] - last_tick["last"], 2)
    last_tick["zero_or_five"] = (int(last_tick["last"]) == last_tick["last"]) and (str(last_tick["last"])[-1] in ["0", "5"])
    last_tick["pressure"] = int(last_tick["bid_size"] - last_tick["ask_size"])
    last_tick["momentum"] = last_tick["last"] - last_tick["open"]

    

