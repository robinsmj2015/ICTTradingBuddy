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


class Plotter:
    def __init__(self, symbol):
        self.buddy = None
        self.symbol = symbol

    # ============ Helper Functions ============
    @staticmethod
    def plot_candles(df, title):
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'], high=df['high'], low=df['low'], close=df['close'],
            increasing_line_color='green', decreasing_line_color='red'))
        fig.update_layout(title=title, xaxis_rangeslider_visible=False)
        return fig

    @staticmethod
    def plot_volume(df, title):
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.index, y=df['volume'], marker_color='gray'))
        fig.update_layout(title=title, yaxis_title='Volume')
        return fig
    
    @staticmethod
    def plot_speedometer(val, atr):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            title={'text': f"Recommendation Strength (ATR: {atr})"},
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
    def plot_indicator_bars(indicators_dict):
        df = pd.DataFrame(list(indicators_dict.items()), columns=['Indicator', 'Score'])
        colors = df['Score'].apply(lambda v: 'green' if v > 0 else 'red' if v < 0 else 'gray')
        fig = px.bar(df, x='Score', y='Indicator', orientation='h', color=colors,
                    color_discrete_sequence=colors, title="Subindicator Scores")
        fig.update_layout(showlegend=False, xaxis_range=[-10, 10])
        return fig
    
    @staticmethod
    def plot_balance(df, start_balance):
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

    # ============ Streamlit Layout ============
    def render_all(self):

        

        unique_suffix = str(int(time.time() * 1000)) 

        rec = self.buddy.recommendation

        st.write("ICT Markers:")
        for k, v in rec.ict_markers.items():
            st.write(k, v)


        col1, col2, col3 = st.columns(3)

        with col1:
            st.plotly_chart(self.plot_candles(self.buddy.candles[1].trackers[0].df.tail(15), "1m Price"), use_container_width=True, key=f"1m price {unique_suffix}")
            st.plotly_chart(self.plot_volume(self.buddy.candles[1].trackers[0].df.tail(15), "1m Volume"), use_container_width=True, key=f"1m volume {unique_suffix}")

        with col2:
            st.plotly_chart(self.plot_candles(self.buddy.candles[3].df.tail(15), "3m Price"), use_container_width=True, key=f"3m price {unique_suffix}")
            st.plotly_chart(self.plot_volume(self.buddy.candles[3].df.tail(15), "3m Volume"), use_container_width=True, key=f"3m volume {unique_suffix}")
        
        with col3:
            st.plotly_chart(self.plot_candles(self.buddy.candles[5].df.tail(15), "5m Price"), use_container_width=True, key=f"5m price {unique_suffix}")
            st.plotly_chart(self.plot_volume(self.buddy.candles[5].df.tail(15), "5m Volume"), use_container_width=True, key=f"5m volume {unique_suffix}")

        #st.plotly_chart(self.plot_candles(self.buddy.candles[15].df.tail(15), "15m Price"), use_container_width=True, key="15m price")
        st.plotly_chart(self.plot_speedometer(rec.val if rec.valid else 0, rec.ict_indicators.get("atr", 0)), use_container_width=True, key=f"speedometer {unique_suffix}")

        bars = rec.ict_indicators.copy() if rec.valid else {}
        bars["indicators"] = rec.other_indicators.get("inds", 0)
        default_keys = ["order_blocks", "liq_sweep", "fvg", "pressure_imbalance", "fv_dislocation", "indicators"]
        for k in default_keys:
            bars.setdefault(k, 0)
        st.plotly_chart(self.plot_indicator_bars(bars), use_container_width=True, key=f"indicators {unique_suffix}")

        st.plotly_chart(
            self.plot_balance(self.buddy.buff.df[self.buddy.buff.df['actual_profit'].notna()], self.buddy.trader.starting_balance),
            use_container_width=True, key=f"balance {unique_suffix}"
        )


