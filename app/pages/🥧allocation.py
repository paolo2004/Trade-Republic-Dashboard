import numpy as np
import plotly.express as px
import streamlit as st
from utils.import_data import check_if_data_loaded, validate_data
from utils.metrics import get_buy_transactions

st.title("Portfolio Allocation Overview")

check_if_data_loaded()
df = st.session_state["df"].copy()
validate_data(df)

st.text("Visual representation of your portfolio allocation based on the latest transactions.")

buy_transactions = get_buy_transactions(df)

# Use a share-weighted price because buy orders can contain different quantities.
buy_transactions["buy_value"] = buy_transactions["price"] * buy_transactions["shares"]

cel1, cel2, cel3 = st.columns(3)
with cel1:
    st.subheader("Total invested amount")
    st.write(
        f"**{-buy_transactions['amount'].sum():.2f} €**"
    )  # negative because buys are negative amounts
with cel2:
    st.subheader("Total number of buy transactions")
    st.write(f"**{len(buy_transactions)}**")
with cel3:
    st.subheader("Number of unique assets")
    st.write(f"**{buy_transactions['name'].nunique()}**")

allocation_by_asset = buy_transactions.groupby(["name", "symbol"], as_index=False).agg(
    total_invested=("amount", "sum"),
    total_shares=("shares", "sum"),
    buy_transactions=("amount", "count"),
    total_buy_value=("buy_value", "sum"),
    total_fee=("fee", "sum"),
    asset_class=("asset_class", "first"),
)

allocation_by_asset["avg_buy_price"] = np.where(
    allocation_by_asset["total_shares"] != 0,
    allocation_by_asset["total_buy_value"] / allocation_by_asset["total_shares"],
    np.nan,
)

col1, col2 = st.columns(2)

with col1:
    allocation_by_asset["total_invested"] = allocation_by_asset["total_invested"].abs()
    st.subheader("Allocation by Asset")
    sorted_allocation = allocation_by_asset.sort_values(by="total_invested", ascending=False)
    display_columns = ["name", "total_invested", "total_shares", "buy_transactions"]
    st.dataframe(sorted_allocation[display_columns])

with col2:
    st.subheader("Allocation over Time")
    allocation_over_time = buy_transactions.groupby("date", as_index=False).agg(
        total_invested=("amount", "sum")
    )
    allocation_over_time["total_invested"] = allocation_over_time["total_invested"].abs()
    st.line_chart(allocation_over_time, x="date", y="total_invested")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Portfolio Allocation")
    fig = px.pie(sorted_allocation, values="total_invested", names="name")
    st.plotly_chart(fig)

with col2:
    st.subheader("Allocation by Asset Class")

    asset_class = df.groupby("asset_class")["amount"].sum().abs().reset_index()

    fig = px.pie(asset_class, names="asset_class", values="amount", hole=0.55)

    st.plotly_chart(fig)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Stock Allocation")
    stock_allocation = sorted_allocation[sorted_allocation["asset_class"] == "STOCK"].copy()
    if not stock_allocation.empty:
        fig_stock = px.pie(stock_allocation, values="total_invested", names="name")
        st.plotly_chart(fig_stock)
    else:
        st.info("No stock transactions found.")

with col2:
    st.subheader("Crypto Allocation")
    crypto_allocation = sorted_allocation[sorted_allocation["asset_class"] == "CRYPTO"].copy()
    if not crypto_allocation.empty:
        fig_crypto = px.pie(crypto_allocation, values="total_invested", names="name")
        st.plotly_chart(fig_crypto)
    else:
        st.info("No crypto transactions found.")
