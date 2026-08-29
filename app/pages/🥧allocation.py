import numpy as np
import plotly.express as px
import streamlit as st
from utils.import_data import check_if_data_loaded, validate_data
from utils.metrics import get_trades_transactions, add_sector_column, calculate_sector_allocation

st.title("Portfolio Allocation Overview")

check_if_data_loaded()
df = st.session_state["df"].copy()
validate_data(df)

st.text("Visual representation of your portfolio allocation based on the latest transactions.")

trade_transactions = get_trades_transactions(df)

# Use a share-weighted price because buy orders can contain different quantities.
trade_transactions["trade_value"] = trade_transactions["price"] * trade_transactions["shares"]

cel1, cel2, cel3 = st.columns(3)
with cel1:
    st.subheader("Total invested amount")
    st.write(
        f"**{-trade_transactions['amount'].sum():.2f} €**"
    )  # negative because buys are negative amounts
with cel2:
    st.subheader("Total number of trades transactions")
    st.write(f"**{len(trade_transactions)}**")
with cel3:
    st.subheader("Number of unique assets")
    st.write(f"**{trade_transactions['name'].nunique()}**")

allocation_by_asset = trade_transactions.groupby(["name", "asset_class","ticker"], as_index=False).agg(
    total_invested=("amount", "sum"),
    total_shares=("shares", "sum"),
    number_of_trade_transactions=("amount", "count"),
    total_trade_value=("trade_value", "sum"),
    total_fee=("fee", "sum"),
    asset_class=("asset_class", "first"),
)

allocation_by_asset["avg_buy_price"] = np.where(
    allocation_by_asset["total_shares"] != 0,
    allocation_by_asset["total_trade_value"] / allocation_by_asset["total_shares"],
    np.nan,
)

col1, col2 = st.columns(2)

with col1:
    allocation_by_asset["total_invested"] = allocation_by_asset["total_invested"].abs()
    allocation_by_asset = add_sector_column(allocation_by_asset)
    sector_allocation = calculate_sector_allocation(allocation_by_asset)
    st.subheader("Allocation by Asset")
    sorted_allocation = allocation_by_asset.sort_values(by="total_invested", ascending=False)
    display_columns = ["name", "total_invested", "total_shares", "number_of_trade_transactions", "sector"]
    st.dataframe(
        sorted_allocation[display_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn(
                "Asset",
            ),
            "total_invested": st.column_config.NumberColumn(
                "Total invested",
                format="€%.2f",
            ),
            "total_shares": st.column_config.NumberColumn(
                "Total shares",
                format="%.2f",
            ),
            "number_of_trade_transactions": st.column_config.NumberColumn(
                "Number of trades",
                format="%d",
            ),
            "sector": st.column_config.TextColumn(
                "Sector",
            ),
        },
    )

with col2:
    st.subheader("Allocation over Time")
    allocation_over_time = trade_transactions.groupby("date", as_index=False).agg(
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

columns = st.columns(2)
with columns[0]:
    st.subheader("Allocation by Sector")
    st.dataframe(
        sector_allocation,
        use_container_width=True,
        hide_index=True,
        column_config={
            "sector": "Sector",
            "amount": st.column_config.NumberColumn(
                "Amount invested",
                format="€%.2f",
            ),
            "assets": st.column_config.NumberColumn(
                "Number of assets",
                format="%d",
            ),
            "percentage": st.column_config.NumberColumn(
                "Portfolio share",
                format="%.2f%%",
            ),
        },
    )

with columns[1]:
    sector_figure = px.pie(
        sector_allocation,
        values="amount",
        names="sector",
        hole=0.2,
        title="Portfolio Allocation by Sector",
    )

    sector_figure.update_traces(
        textposition="inside",
        textinfo="label+percent",
    )
    sector_figure.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False,
    )

    st.plotly_chart(sector_figure, use_container_width=True)


with st.expander("Show raw data"):
    st.dataframe