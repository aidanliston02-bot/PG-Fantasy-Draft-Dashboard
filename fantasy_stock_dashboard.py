# fantasy_stock_dashboard.py

import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

# --- CONFIG ---
START_TIME = datetime.datetime(2025, 8, 4, 9, 30)  # Monday 9:30am EST
END_TIME = datetime.datetime(2025, 8, 8, 16, 0)    # Friday 4:00pm EST

# Load participant picks and starting prices
# Format: name,ticker,type,start_price
@st.cache_data
def load_data():
    return pd.read_csv("starting_prices.csv")

def get_current_price(ticker, asset_type):
    if asset_type == "stock" or asset_type == "crypto":
        try:
            data = yf.Ticker(ticker).history(period="1d")
            return data["Close"].iloc[-1]
        except:
            return None

st.set_page_config(page_title="Fantasy Draft Order Tracker", layout="wide")
st.title("🏈 Fantasy Draft Order Tracker")
st.markdown("""
Track your stock/crypto pick performance from **Monday 8/4 9:30am** to **Friday 8/8 4:00pm**.

Data updates each time the page loads.
""")

# Load starting data
df = load_data()

# Fetch live prices and calculate change
results = []
for _, row in df.iterrows():
    current_price = get_current_price(row["ticker"], row["type"])
    if current_price is not None:
        pct_change = (current_price - row["start_price"]) / row["start_price"] * 100
        results.append({
            "name": row["name"],
            "ticker": row["ticker"],
            "start_price": row["start_price"],
            "current_price": round(current_price, 2),
            "pct_change": round(pct_change, 2)
        })

results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by="pct_change", ascending=False).reset_index(drop=True)
results_df["rank"] = results_df.index + 1

# Leaderboard Table at the top
st.subheader("🏆 Live Leaderboard")
st.dataframe(results_df[["rank", "name", "ticker", "start_price", "current_price", "pct_change"]], hide_index=True, use_container_width=True)

# Footer
st.caption("Stock starting prices are taken from Yahoo finance opening price on 8/4")
