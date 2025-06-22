"""
Main real-time trading loop.

This script performs the following:
1. Scrapes daily pivot levels from TradingView (unless in test mode).
2. Continuously processes each equity symbol in a loop.
   - For each symbol: retrieves RTD data, updates indicators, evaluates trade signals, and refreshes the UI if enabled.

Dependencies:
    - `Processor.process_symbol`: Handles all trading logic for a given symbol.
    - `Setup`: Contains configuration, symbol definitions, buddies, scraper, and UI flag.
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
    st.warning("⚠️ Session was reset — dashboard restarted. Reinitializing data... This will take ~120 seconds")


st_autorefresh(interval=10 * 1000, key="refresh")  # every 10 seconds


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
tab1, = st.tabs(["Live View"])

# ------------------------ Main Refreshing Logic ------------------------
with tab1:
    with st.empty().container():
        st.subheader("Live Data Simulation")

        # Short loop to update a few times before refreshing
        for _ in range(5):
            process_symbol(buddy)
            time.sleep(2)

        with open("buddy.pkl", "wb") as f:
                pickle.dump(buddy, f)
        
        
        #st.rerun()
        st.markdown(f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')} UTC")
        buddy.plotter.render_all()  
