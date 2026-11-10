import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Nifty 50 Dashboard", layout="wide")
st.title("📈 Stock Performance Dashboard")

@st.cache_data
def fetch_data():
    conn = sqlite3.connect('stock_database.db')
    df = pd.read_sql_query("SELECT * FROM stock_data", conn)
    conn.close()
    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = fetch_data()
except Exception as e:
    st.error("Database not found. Please run stock.py first.")
    st.stop()

# Calculate Metrics
summary = df.groupby('Symbol').agg(
    Start_Price=('open', 'first'),
    End_Price=('close', 'last'),
    Volatility=('Daily_Return', 'std')
).reset_index()

summary['Yearly_Return_%'] = ((summary['End_Price'] - summary['Start_Price']) / summary['Start_Price']) * 100
green_stocks = summary[summary['Yearly_Return_%'] > 0]
red_stocks = summary[summary['Yearly_Return_%'] <= 0]

st.header("📊 Market Overview")
c1, c2, c3 = st.columns(3)
c1.metric("Green Stocks (Profit)", len(green_stocks))
c2.metric("Red Stocks (Loss)", len(red_stocks))
c3.metric("Avg Volatility", f"{summary['Volatility'].mean():.4f}")

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 Top 10 Green Stocks")
    top_green = green_stocks.nlargest(10, 'Yearly_Return_%')
    fig1 = px.bar(top_green, x='Symbol', y='Yearly_Return_%', color='Yearly_Return_%', color_continuous_scale='Greens')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🔴 Top 10 Loss Stocks")
    top_red = red_stocks.nsmallest(10, 'Yearly_Return_%')
    fig2 = px.bar(top_red, x='Symbol', y='Yearly_Return_%', color='Yearly_Return_%', color_continuous_scale='Reds_r')
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("⚠️ Top 10 Volatile Stocks (High Risk)")
top_volatile = summary.nlargest(10, 'Volatility')
fig3 = px.bar(top_volatile, x='Symbol', y='Volatility', color_discrete_sequence=['orange'])
st.plotly_chart(fig3, use_container_width=True)