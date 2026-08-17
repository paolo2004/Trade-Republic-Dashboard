import plotly.express as px
import streamlit as st
from utils.import_data import check_if_data_loaded, validate_data

st.title("Expenses")

check_if_data_loaded()
df = st.session_state["df"].copy()
validate_data(df)

expenses = df[df["type"] == "CARD_TRANSACTION"].copy()
expenses["amount"] = expenses["amount"].abs()  # Convert to positive values for display

if expenses.empty:
    st.info("No expense transactions found in the uploaded data.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("Total Expenses")
    st.write(f"**{expenses['amount'].sum():.2f} €**")

with col2:
    st.subheader("Number of Expenses")
    st.write(f"**{len(expenses)}**")

with col3:
    st.subheader("Total Fees")
    st.write(f"**{expenses['fee'].sum():.2f} €**")

with col4:
    st.subheader("Total Taxes")
    st.write(f"**{expenses['tax'].sum():.2f} €**")

col1, col2 = st.columns([0.6, 0.4])
with col1:
    expenses_over_time = expenses.groupby("month", as_index=False)["amount"].sum()
    st.subheader("Expenses Over Time")
    st.line_chart(expenses_over_time, x="month", y="amount")

with col2:
    st.subheader("Expenses by Category(Top 15)")
    expenses_by_category = (
        expenses.groupby("name", as_index=False)
        .agg(total_expenses=("amount", "sum"))
        .sort_values(by="total_expenses", ascending=False)
        .head(15)
    )
    fig = px.pie(expenses_by_category, values="total_expenses", names="name")
    st.plotly_chart(fig)

st.subheader("Detailed Expenses Data")
columns_to_display = [
    "date",
    "name",
    "amount",
    "currency",
]
st.dataframe(expenses[columns_to_display])
