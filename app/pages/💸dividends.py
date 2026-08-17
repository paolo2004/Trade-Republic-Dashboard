import plotly.express as px
import streamlit as st
from utils.import_data import check_if_data_loaded, validate_data

st.title("Dividends")

check_if_data_loaded()

df = st.session_state["df"]
validate_data(df)
dividends = df[df["type"] == "DIVIDEND"].copy()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.write(f"**Total Dividends** \n\n  {dividends['amount'].sum():.2f} € ")

with col2:
    st.write(f"**Taxes** \n\n  {dividends['tax'].sum():.2f} € ")

with col3:
    st.write(f"**Payments** \n\n  {len(dividends)}")

with col4:
    st.write(f"**Assets** \n\n  {len(set(dividends['name']))}")

col1, col2 = st.columns(2)
with col1:
    st.subheader("All Dividends payments")
    st.dataframe(
        dividends[
            [
                "date",
                "name",
                "shares",
                "amount",
                "tax",
            ]
        ]
    )
with col2:
    st.subheader("Dividends Over Time")
    dividends_over_time = dividends.groupby("date", as_index=False)["amount"].sum()
    st.line_chart(dividends_over_time, x="date", y="amount")

col1, col2 = st.columns([0.6, 0.4])

with col1:
    monthly = dividends.groupby("month", as_index=False)["amount"].sum()
    st.subheader("Monthly Dividends")
    st.bar_chart(monthly, x="month", y="amount")  #

    dividends_by_asset = dividends.groupby(["name", "symbol"], as_index=False).agg(
        total_dividends=("amount", "sum"),
        total_tax=("tax", "sum"),
        payments=("amount", "count"),
    )

with col2:
    st.subheader("Dividends by Asset")
    # prepare formatted hover fields to avoid missing values and ensure proper line breaks
    dividends_by_asset["total_tax"] = (
        dividends_by_asset["total_tax"].fillna(0).map(lambda x: f"{x:.2f}")
    )
    dividends_by_asset["payments"] = (
        dividends_by_asset["payments"].fillna(0).astype(int).astype(str)
    )
    fig = px.pie(
        dividends_by_asset,
        names="name",
        values="total_dividends",
        hover_data=["total_tax", "payments"],
    )
    st.plotly_chart(fig, use_container_width=True)
