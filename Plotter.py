"""
Plotly version of real-time trading visualization, adapted from Matplotlib-based Plotter.
Displays:
    - Candlestick charts for 1m, 5m, 15m intervals.
    - Subindicator bar chart.
    - Speedometer for trade confidence.
    - Equity curve.
This script is compatible with Streamlit and Render.com.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
import time
from typing import Dict, List, Any


class Plotter:
    """
    Plotter class for rendering live trading visualizations using Plotly and Streamlit.

    Attributes:
        buddy: Object containing trade data and signals.
        symbol: Trading symbol being visualized.
    """

    def __init__(self, symbol: str) -> None:
        """
        Initialize Plotter.

        Args:
            symbol (str): The trading symbol to visualize.
        """
        self.buddy = None
        self.symbol = symbol

    @staticmethod
    def plot_candles(df: pd.DataFrame, title: str) -> go.Figure:
        """
        Generate a candlestick chart.

        Args:
            df (pd.DataFrame): DataFrame containing OHLC data.
            title (str): Title of the plot.

        Returns:
            go.Figure: Plotly candlestick chart.
        """
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'], high=df['high'], low=df['low'], close=df['close'],
            increasing_line_color='green', decreasing_line_color='red'))
        fig.update_layout(title=title, xaxis_rangeslider_visible=False, xaxis_title="Time (UTC)", yaxis_title="Price ($)")
        return fig

    @staticmethod
    def plot_volume(df: pd.DataFrame, title: str) -> go.Figure:
        """
        Generate a volume bar chart.

        Args:
            df (pd.DataFrame): DataFrame containing volume data.
            title (str): Title of the chart.

        Returns:
            go.Figure: Plotly bar chart.
        """
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.index, y=df['volume'], marker_color='gray'))
        fig.update_layout(title=title, yaxis_title='Volume', xaxis_title='Time (UTC)')
        return fig

    @staticmethod
    def plot_pressure_meter(p: float) -> go.Figure:
        """
        Plot a gauge showing pressure imbalance.

        Args:
            p (float): Pressure value (bid size - ask size).

        Returns:
            go.Figure: Gauge plot.
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=p,
            title={'text': "Pressure (Bid size - ask size)"},
            gauge={
                'axis': {'range': [-10, 10]},
                'bar': {'color': "black"},
                'steps': [
                    {'range': [-10, -5], 'color': "red"},
                    {'range': [-5, 5], 'color': "gold"},
                    {'range': [5, 10], 'color': "green"},
                ]
            }
        ))
        return fig

    @staticmethod
    def plot_atr_meter(atr: float) -> go.Figure:
        """
        Plot an ATR (Average True Range) gauge.

        Args:
            atr (float): ATR value.

        Returns:
            go.Figure: ATR gauge.
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=atr,
            title={'text': "ATR"},
            gauge={
                'axis': {'range': [0, 128]},
                'bar': {'color': "black"},
                'steps': [
                    {'range': [0, 16], 'color': "white"},
                    {'range': [16, 32], 'color': "lightgray"},
                    {'range': [32, 64], 'color': "gray"},
                    {'range': [64, 128], 'color': "darkgray"},
                ]
            }
        ))
        return fig

    @staticmethod
    def plot_speedometer(val: float) -> go.Figure:
        """
        Plot recommendation strength on a gauge.

        Args:
            val (float): Recommendation strength.

        Returns:
            go.Figure: Gauge chart.
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            title={'text': "Recommendation Strength"},
            gauge={
                'axis': {'range': [-10, 10]},
                'bar': {'color': "black"},
                'steps': [
                    {'range': [-10, -5], 'color': "red"},
                    {'range': [-5, 5], 'color': "gold"},
                    {'range': [5, 10], 'color': "green"},
                ]
            }
        ))
        return fig

    @staticmethod
    def plot_indicator_bars(indicators_dict: Dict[str, float]) -> go.Figure:
        """
        Create a horizontal bar chart of subindicator scores.

        Args:
            indicators_dict (Dict[str, float]): Dictionary of indicator names and their scores.

        Returns:
            go.Figure: Horizontal bar chart.
        """
        df = pd.DataFrame(list(indicators_dict.items()), columns=['Indicator', 'Score'])
        df['Color'] = df['Score'].apply(lambda v: 'green' if v > 0 else 'red' if v < 0 else 'gray')

        fig = px.bar(
            df,
            x='Score',
            y='Indicator',
            orientation='h',
            color='Indicator',
            color_discrete_map={row['Indicator']: row['Color'] for _, row in df.iterrows()},
            title="Subindicator Scores"
        )
        fig.update_layout(
            showlegend=False,
            xaxis_title="Score",
            yaxis_title="Indicator",
            xaxis_range=[-10, 10]
        )
        return fig

    @staticmethod
    def plot_balance(df: pd.DataFrame, start_balance: float) -> go.Figure:
        """
        Plot running account balance based on cumulative profit.

        Args:
            df (pd.DataFrame): DataFrame with 'actual_profit' column.
            start_balance (float): Starting balance for the trading account.

        Returns:
            go.Figure: Line chart of balance over time.
        """
        if df.empty:
            return go.Figure()
        df = df.copy()
        df['balance'] = df['actual_profit'].cumsum() + start_balance
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=pd.to_datetime(df.index), y=df['balance'],
                                 mode='lines+markers', line=dict(color='cyan')))
        fig.update_layout(title="Balance Over Time", yaxis_title="Balance ($)",
                          xaxis_title="Time")
        return fig

    @staticmethod
    def plot_zone_ladder(zones, title: str) -> go.Figure:
        """
        Create a ladder-style vertical zone chart for ICT markers.

        Args:
            zones (List[Dict[str, float]]): List of zone dictionaries with 'low' and 'high' values.
            title (str): Chart title.

        Returns:
            go.Figure: Ladder zone chart.
        """

        reds, greens = [], []

        if title == "Order Blocks":
            # [{"high": x, "low": y}, ...]
            for z in zones:
                reds.append(z["low"])
                greens.append(z["high"])
            
        elif title == "Liquidity Sweeps":
            # {"high": [x, y, z], "low": [a, b, c]}
            reds = zones.get("short", [])
            greens = zones.get("long", []) 

        elif title == "FVGs":
            # {short: [(low1, high1)...], long: [(low2, high2)...]}
            if zones:
                st.write(zones)
            for position in zones:
                for tup in position:
                    reds.append(tup[0])
                    if len(tup) == 2:
                        greens.append(tup[1])
        
        fig = go.Figure()

        if not reds and not greens:
            return fig
        

        min_red, min_green, max_red, max_green = float("inf"),  float("inf"), float("-inf"), float("-inf")
        if reds:
            min_red = min(reds)
            max_red = max(reds)
        
        if greens:
            min_green = min(greens)
            max_green = max(greens)

        
        min_price = min(min_red, min_green) - 2
        max_price = max(max_red, max_green) + 2

        for red in reds:
            fig.add_trace(go.Scatter(x=[0, 1], y=[red, red], mode='lines', line=dict(color='red', width=6), showlegend=False))
        
        for green in greens:
            fig.add_trace(go.Scatter(x=[0, 1], y=[green, green], mode='lines', line=dict(color='green', width=6), showlegend=False))

        fig.update_layout(
            title=title,
            xaxis=dict(visible=False),
            yaxis=dict(autorange=False, range=[min_price, max_price], title='Price', tickmode='linear', dtick=1),
            height=500,
            margin=dict(l=20, r=40, t=40, b=20)
        )
        return fig

    def render_all(self) -> None:
        """
        Render all visual components in Streamlit layout including:
        - Candlesticks
        - Volume
        - ICT zone ladders
        - Gauges for recommendation, ATR, and pressure
        - Indicator bar scores

        Args:
            None

        Returns:
            None
        """
        if len(self.buddy.candles[1].trackers[0].df) < self.buddy.data_gather_time:
            st.write(".")
            return

        unique_suffix = str(int(time.time() * 1000)) 
        rec = self.buddy.recommendation

        # Candlestick and Volume Charts
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.empty():
                st.plotly_chart(self.plot_candles(self.buddy.candles[1].trackers[0].df.tail(15), "1m Price"), use_container_width=True, key=f"1m price {unique_suffix}")
                st.plotly_chart(self.plot_volume(self.buddy.candles[1].trackers[0].df.tail(15), "1m Volume"), use_container_width=True, key=f"1m volume {unique_suffix}")
        with col2:
            with st.empty():
                st.plotly_chart(self.plot_candles(self.buddy.candles[3].df.tail(15), "3m Price"), use_container_width=True, key=f"3m price {unique_suffix}")
                st.plotly_chart(self.plot_volume(self.buddy.candles[3].df.tail(15), "3m Volume"), use_container_width=True, key=f"3m volume {unique_suffix}")
        with col3:
            with st.empty():
                st.plotly_chart(self.plot_candles(self.buddy.candles[5].df.tail(15), "5m Price"), use_container_width=True, key=f"5m price {unique_suffix}")
                st.plotly_chart(self.plot_volume(self.buddy.candles[5].df.tail(15), "5m Volume"), use_container_width=True, key=f"5m volume {unique_suffix}")

        # ICT Zones
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.empty():
                st.plotly_chart(self.plot_zone_ladder(rec.ict_markers["obs"], "Order Blocks"), use_container_width=True, key=f"OB {unique_suffix}")
        with c2:
            with st.empty():
                st.plotly_chart(self.plot_zone_ladder(rec.ict_markers["liq_pools"], "Liquidity Sweeps"), use_container_width=True, key=f"LS {unique_suffix}")
        with c3:
            with st.empty():
                st.plotly_chart(self.plot_zone_ladder(rec.ict_markers["fvg_zones"], "FVGs"), use_container_width=True, key=f"FVG {unique_suffix}")

        # Gauges
        g1, g2, g3 = st.columns(3)
        with g1:
            with st.empty():
                st.plotly_chart(self.plot_speedometer(rec.val or 0), use_container_width=True, key=f"speedometer {unique_suffix}")
        with g2:
            with st.empty():
                st.plotly_chart(self.plot_atr_meter(rec.ict_indicators.get("atr", 0)), use_container_width=True, key=f"atr_meter {unique_suffix}")
        with g3:
            with st.empty():
                st.plotly_chart(self.plot_pressure_meter(rec.ict_indicators.get("pressure_imbalance", 1)), use_container_width=True, key=f"pressure meter {unique_suffix}")

        # Indicator Bars
        bars = rec.ict_indicators.copy() or {}
        bars["indicators"] = rec.other_indicators.get("inds", 0)
        default_keys = ["fv_dislocation", "indicators"]
        for k in default_keys:
            bars.setdefault(k, 0)
        with st.empty():
            st.plotly_chart(self.plot_indicator_bars(bars), use_container_width=True, key=f"indicators {unique_suffix}")

