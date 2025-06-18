import streamlit as st
import pandas as pd

st.set_page_config(page_title="Trading Buddy", layout="wide")

st.title("📈 ICT Trading Buddy Dashboard")

tab1, tab2 = st.tabs(["Live View", "Demo with Static Data"])

with tab1:
    st.subheader("Live Trade Visualization")
    # Call live components or placeholder
    # e.g. st.line_chart(...) or custom plot
