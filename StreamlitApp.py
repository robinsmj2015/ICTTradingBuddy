"""
Main real-time trading loop.

This script performs the following:
1. Scrapes daily pivot levels from TradingView (unless in test mode).
2. Continuously processes each equity symbol in a loop.
   - For each symbol: retrieves RTD data, updates indicators, evaluates trade signals, and refreshes the UI if enabled.

Dependencies:
    - Processor.process_symbol: Handles all trading logic for a given symbol.
    - Setup: Contains configuration, symbol definitions, buddies, scraper, and UI flag.
"""

# https://icttradingbuddy.onrender.com
# https://dashboard.render.com/web/srv-d190thvdiees73ad5gbg/deploys/dep-d192aa3uibrs73boejjg

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pickle
from Processor import process_symbol
import datetime
import os


# ------------------- Reset warning-------------------

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.cold_start = True
else:
    st.session_state.cold_start = False

if st.session_state.cold_start:
    st.warning("⚠️ Session was reset — dashboard restarted. Please see the tutorial tab while data loads.")


st_autorefresh(interval=30 * 1000, key="refresh")  # every 30 seconds


# --------------------------------- Reset at midnight ------------------------------

def reset_at_midnight():
    """" Resets app at midnight -- prevent excessive memory storage
    """
    now = datetime.datetime.now()
    if now.hour == 0 and now.minute == 0:
        try:
            os.remove("buddy.pkl")
        except FileNotFoundError:
            pass
        st.session_state.clear()
        #st.rerun()


reset_at_midnight()

# ------------------------ Persistent Buddy Instance ------------------------
if "buddy" not in st.session_state:
    try:
        with open("buddy.pkl", "rb") as f:
            st.session_state.buddy = pickle.load(f)
    except Exception:
        from Setup import b  # Import only on cold start
        st.session_state.buddy = b
        

buddy = st.session_state.buddy

# ------------------------ Streamlit UI Config ------------------------
st.set_page_config(page_title="Trading Buddy", layout="wide")
st.title("📈 ICT Trading Buddy Dashboard")
tab1, tab2 = st.tabs(["Tutorial: Static", "Data simulation: Live"])

# ------------------------ Main Refreshing Logic ------------------------

# tutorial
with tab1:

    st.subheader("Candles")
    st.write("1m, 3m and 5m candles update every 30 sec. Last price shown dashed in blue.")
    st.image("Screenshots/candles.png", use_container_width=True)

    st.subheader("Volume")
    st.write("1m, 3m and 5m candle volumes (update every 30 sec).")
    st.image("Screenshots/volume_pic.png", use_container_width=True)

    st.subheader("Inner Circle Trading Indicators")
    st.write("Order Blocks are zones on a chart where large institutions have placed significant buy or sell orders, often marking the origin of a strong price move. These areas are likely to act as support or resistance when price revisits them.")
    st.write("Liquidity Sweeps happen when price spikes beyond a recent high or low, triggering stop-loss orders or attracting breakout traders. These moves are often followed by a sharp reversal, as smart money uses the sweep to fill their positions.")
    st.write("Fair Value Gaps (FVGs) are imbalances in price action where a candle moves so quickly that one side of the order book is skipped, leaving a gap between the high of one candle and the low of the next. Price often returns to these gaps to rebalance liquidity.")
    st.image("Screenshots/ict.png", use_container_width=True)

    st.subheader("Speedometers")
    st.write("**Recommendation Strength** – Shows the aggregated trade signal score from all indicators, where +10 is a strong long and -10 is a strong short.")
    st.write("**ATR** – Displays the Average True Range, a volatility measure showing the average range of recent candles.")
    st.write("**Pressure (Bid size - Ask size)** – Measures real-time order book pressure, where negative values suggest more selling pressure.")
    st.image("Screenshots/big3.png", use_container_width=True)

    
    st.subheader("Other indicators")
    st.write("**VWAP** – Assesses price in relation to the Volume-Weighted Average Price.")
    st.write("**EMA** – Compares short and long Exponential Moving Averages to determine trend direction.")
    st.write("**Session Momentum** – Reflects price movement strength within the current trading session.")
    st.write("**Stochastic RSI** – Evaluates the relative position of RSI to detect overbought/oversold conditions.")
    st.write("**RSI** – The Relative Strength Index indicates trend strength and potential reversals.")
    st.write("**FV Dislocation** – Measures deviation from fair value using gaps in pricing.")
    st.image("Screenshots/little_inds.png", use_container_width=True)

    st.markdown("""📚 References & Attribution: \nThis project incorporates concepts inspired by Michael J. Huddleston, also known as The Inner Circle Trader (ICT).\nFor official educational material, please visit:
🔗 TheInnerCircleTrader.com\n\nThis project is not affiliated with or endorsed by ICT or Michael J. Huddleston.""")

# Live
with tab2:
    for i in range(9):
        process_symbol(buddy, i)
        time.sleep(2)

    with open("buddy.pkl", "wb") as f:
            pickle.dump(buddy, f)

