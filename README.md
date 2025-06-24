ICT Trading Buddy Dashboard
🚀 **Live Trading Dashboard (Deployed on Render.io)**

📍 URL: https://icttradingbuddy.onrender.com
📂 GitHub: https://github.com/robinsmj2015/ICTTradingBuddy

🔧 Project Overview
ICT Trading Buddy is a real-time trading assistant dashboard designed to visualize key market signals using advanced trading indicators and Smart Money Concepts (SMC). The dashboard is deployed using Docker on Render.io and updates every 30 seconds with live market data and computed signals.

📦 Key Features
- Real-time 1m, 3m, and 5m candlestick charts with volume.
- Advanced ICT concepts: Fair Value Gaps (FVG), Order Blocks, Liquidity Sweeps.
- Custom speedometer indicators for Recommendation Strength, ATR, Pressure, VWAP, EMA, RSI, and more.
- Dockerized deployment for reproducibility and portability.
- Streamlit interface with autorefresh and session persistence.
- Auto-reset at midnight to manage session state and memory.

🧠 Technical Stack
- Python 3.13
- Streamlit (UI and live dashboarding)
- Pandas (data manipulation)
- Plotly (chart rendering)
- Docker (containerized deployment)
- Render.io (hosting)

🗂️ Code Structure
Key components of the app:
- `StreamlitApp.py`: Entry point for the UI, handles refresh, session, and layout.
- `Processor.py`: Core logic for processing symbols and updating live indicators.
- `Setup.py`: Configuration and symbol/buddy initialization.
- `Plotter.py`: Visuals for candles, volumes, zones, and indicators.
- `StratICT.py`: Strategy class combining signals into a recommendation.
- `InnerCircleTradingUtils.py`: ICT concept scoring (FVG, OB, Liquidity).
- `*.py` modules: Dedicated to signal generation, trade logic, and live price tracking.

📊 Indicators & Concepts
- **Order Blocks**: Price zones indicating institutional activity that may act as support/resistance.
- **Fair Value Gaps (FVG)**: Gaps between candles indicating unbalanced liquidity.
- **Liquidity Sweeps**: Temporary moves beyond key highs/lows to trap retail positions.
- **ATR**: Measures market volatility.
- **Bid-Ask Pressure**: Gauges buying vs. selling pressure in the order book.
- **VWAP/EMA/RSI/StochRSI**: Classic technical indicators for directional bias.
- **Session Momentum**: Tracks momentum unique to each trading session.
- **Recommendation Strength**: Composite score from all signals, visualized via speedometer.

🚢 Deployment Details
- Dockerized using `Dockerfile` and `.dockerignore` for efficient build context.
- Auto-refresh every 30 seconds using `streamlit_autorefresh`.
- Streamlit state management using session storage and pickled objects.
- Screenshots included for professional tutorial display on dashboard.

📎 Example Dockerfile Snippet
FROM python:3.13-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "StreamlitApp.py"]

---

📌 Built and maintained by Michael J Robinson as part of an advanced trading system engineering project.
