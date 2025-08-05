# fantasy_stock_dashboard.py

import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import pytz

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
st.title("\U0001F3C8 Fantasy Draft Order Tracker")

# Track last update time
eastern = pytz.timezone('US/Eastern')
now_est = datetime.datetime.now(tz=eastern)
now_formatted = now_est.strftime("%Y-%m-%d %I:%M:%S %p %Z")

st.markdown(f"""
Track your stock/crypto pick performance from **Monday 8/4 9:30am** to **Friday 8/8 4:00pm**.

_Last update: **{now_formatted}**_
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
            "start_price_val": row["start_price"],
            "start_price": f"${row['start_price']:.2f}",
            "current_price_val": current_price,
            "current_price": f"${current_price:.2f}",
            "pct_change_val": pct_change,
            "pct_change": f"{pct_change:.2f}%"
        })

results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by="pct_change_val", ascending=False).reset_index(drop=True)

# Add medals and emoji ranks
def medal(rank):
    return {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, str(rank))

results_df["rank"] = results_df.index + 1
results_df["rank"] = results_df["rank"].apply(medal)

# Conditional styling
def highlight_change(val):
    if isinstance(val, str):
        try:
            val_num = float(val.strip('%'))
            if val_num > 0:
                return 'color: green; font-weight: bold'
            elif val_num < 0:
                return 'color: red;'
        except:
            pass
    return ''

def link_ticker(ticker):
    return ticker

results_df["ticker"] = results_df["ticker"].apply(link_ticker)

# Leaderboard Table at the top
st.subheader("\U0001F3C6 Live Leaderboard")
st.dataframe(
    results_df[["rank", "name", "ticker", "start_price", "current_price", "pct_change"]]
    .style.applymap(highlight_change, subset=["pct_change"]),
    hide_index=True,
    use_container_width=True
)


# Footer
st.caption("Stock starting prices are taken from Yahoo finance opening price on 8/4")
