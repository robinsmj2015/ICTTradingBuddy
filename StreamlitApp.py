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
from Processor import process_symbol
from Setup import buddies
import time


st.set_page_config(page_title="Trading Buddy", layout="wide")

st.title("📈 ICT Trading Buddy Dashboard")

tab1 = st.tabs(["Live View"])

eq = "test"

# ------------------------ Main infinite loop ----------------------------------------------

with tab1:
    st.subheader("Live Trade Visualization")
    # Call live components or placeholder
    # e.g. st.line_chart(...) or custom plot
    while True:
        process_symbol(buddies[eq])
        time.sleep(1)  # space updates between symbols

