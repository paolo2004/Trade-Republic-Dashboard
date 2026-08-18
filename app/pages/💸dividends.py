import plotly.express as px
import streamlit as st
import pandas as pd
from utils.import_data import check_if_data_loaded, validate_data

st.set_page_config(page_title="Dividends", page_icon="💸", layout="wide")
st.title("Dividends")
st.caption("Track your dividend income, taxes, payment activity, and income sources.")


check_if_data_loaded()

df = st.session_state["df"]
validate_data(df)
dividends = df[df["type"] == "DIVIDEND"].copy()

if dividends.empty:
    st.info("No dividend payments were found in the currently loaded export.")
    st.stop()

min_date = dividends["date"].min()
max_date = dividends["date"].max()
dividends["net_income"] = dividends["amount"] + dividends["tax"]

st.sidebar.header("Dividend filters")

period = st.sidebar.selectbox(
    "Period", 
    ["All time", "Current year", "Last 12 months", "Custom range"],
)

if period == "Current year":
    filtered_dividends = dividends[dividends["date"].dt.year == max_date.year].copy()
elif period == "Last 12 months":
    start_date = max_date - pd.DateOffset(months=12)
elif period == "Custom range":
    selected_dates = st.sidebar.date_input(
        "Select date range",
        value = (min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )
    if len(selected_dates) != 2:
        st.warning("Please select a start and a end date")
        st.stop()

    start_date, end_date = selected_dates
    filtered_dividends = dividends[
        (dividends["date"].dt.date >= start_date)
        & (dividends["date"].dt.date <= end_date)
    ].copy()
else:
    filtered_dividends = dividends.copy()

if filtered_dividends.empty:
    st.warning("No dividend payments were found for the selected period.")
    st.stop()

total_gross = filtered_dividends["amount"].sum()
total_tax = filtered_dividends["tax"].abs().sum()
total_net = filtered_dividends["net_income"].sum()
payments = len(filtered_dividends)
paying_assets = filtered_dividends["name"].nunique()
average_payment = total_net / payments if payments else 0
effective_tax_rate = total_tax / total_gross if total_gross else 0

monthly_income = (
    filtered_dividends.groupby("month", as_index=False)
    .agg(
        gross_dividends=("amount", "sum"),
        taxes_paid=("tax", lambda values: values.abs().sum()),
        net_dividends=("net_income", "sum"),
    )
    .sort_values("month")
)

best_month = monthly_income.loc[monthly_income["net_dividends"].idxmax()]
st.subheader ("Dividends overview")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Net dividends", f"€{total_net:,.2f}")
with col2:
    st.metric("Gross dividends", f"€{total_gross:,.2f}")
with col3:
    st.metric("Taxes paid", f"€{total_tax:,.2f}")
with col4:
    st.metric("Payments", payments)
with col5:
    st.metric("Paying assets", paying_assets)
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Average net payment", f"€{average_payment:,.2f}")
with col2:
    st.metric("Effective tax rate", f"{effective_tax_rate:.1%}")
with col3:
    st.metric(
        "Best month",
        best_month["month"],
        delta=f"€{best_month['net_dividends']:,.2f} net",
    )
st.divider() #st.markdown("---")

left_column, right_column = st.columns(2)
with left_column:
    st.subheader("Monthly net dividend income")

    monthly_net_chart = px.bar(
        monthly_income,
        x="month",
        y="net_dividends",
        labels= {"month": "Month", "net_dividends": "Net dividends (€)"},
        color_discrete_sequence=["#4CAF50"],
    )
    monthly_net_chart.update_layout(
        xaxis_title=None,
        yaxis_title="Net dividends (€)",
        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(monthly_net_chart, use_container_width=True)

with right_column:
    st.subheader("Gross Dividends vs. taxes")

    monthly_gross_tax_chart = px.bar(
        monthly_income,
        x="month",
        y=["gross_dividends", "taxes_paid"],
        barmode="group",
        labels={
            "month": "Month",
            "value": "Amount (€)",
            "variable": "Metric",
        },
        color_discrete_map={
            "gross_dividends": "#2196F3",
            "taxes_paid": "#F44336",
        },
    )
    monthly_gross_tax_chart.update_layout(
        xaxis_title=None,
        yaxis_title="Amount (€)",
        legend_title=None,
        margin=dict(l=0, r=0, t=20, b=0),
    )
    monthly_gross_tax_chart.for_each_trace(
        lambda trace: trace.update(
            name="Gross dividends" if trace.name == "gross_dividends" else "Taxes paid"
        )
    )
    st.plotly_chart(monthly_gross_tax_chart, use_container_width=True)

asset_summary = (
    filtered_dividends.groupby(["name", "symbol"], as_index=False)
    .agg(
        gross_dividends=("amount", "sum"),
        taxes_paid=("tax", lambda values: values.abs().sum()),
        net_dividends=("net_income", "sum"),
        payments=("amount", "count"),
        last_payment=("date", "max"),
    )
    .sort_values("net_dividends", ascending=False)
)
asset_summary["average_payment"] = (
    asset_summary["net_dividends"] / asset_summary["payments"]
)

left_column, right_column = st.columns([0.6, 0.4])

with left_column:
    st.subheader("Top dividend-paying assets")

    top_assets = asset_summary.head(5).sort_values("net_dividends")

    top_assets_chart = px.bar(
        top_assets,
        x="net_dividends",
        y="name",
        orientation="h",
        labels={"net_dividends": "Net dividends (€)", "name": "Asset"},
        color="net_dividends",
        color_continuous_scale="Greens",
    )
    top_assets_chart.update_layout(
        coloraxis_showscale=False,
        yaxis_title=None,
        xaxis_title="Net dividends (€)",
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(top_assets_chart, use_container_width=True)

with right_column:
    st.subheader("Income distribution")

    distribution_chart = px.pie(
        asset_summary,
        names="name",
        values="net_dividends",
        hole=0.55,
    )
    distribution_chart.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Net dividends: €%{value:,.2f}<extra></extra>",
    )
    distribution_chart.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False,
    )
    st.plotly_chart(distribution_chart, use_container_width=True)

st.divider()

st.subheader("Dividend income by asset")

display_summary = asset_summary[
    [
        "name",
        "gross_dividends",
        "taxes_paid",
        "net_dividends",
        "payments",
        "average_payment",
        "last_payment",
    ]
].copy()

st.dataframe(
    display_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "name": "Asset",
        "gross_dividends": st.column_config.NumberColumn(
            "Gross dividends",
            format="€%.2f",
        ),
        "taxes_paid": st.column_config.NumberColumn(
            "Taxes paid",
            format="€%.2f",
        ),
        "net_dividends": st.column_config.NumberColumn(
            "Net dividends",
            format="€%.2f",
        ),
        "payments": st.column_config.NumberColumn("Payments", format="%d"),
        "average_payment": st.column_config.NumberColumn(
            "Average payment",
            format="€%.2f",
        ),
        "last_payment": st.column_config.DateColumn(
            "Last payment",
            format="DD MMM YYYY",
        ),
    },
)


with st.expander("Show raw dividend transactions"):
    raw_dividends = filtered_dividends[
        ["date", "name", "symbol", "shares", "amount", "tax", "net_income", "currency"]
    ].sort_values("date", ascending=False)

    st.dataframe(
        raw_dividends,
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
            "name": "Asset",
            "symbol": "Symbol / ISIN",
            "shares": st.column_config.NumberColumn("Shares", format="%.4f"),
            "amount": st.column_config.NumberColumn("Gross dividend", format="€%.2f"),
            "tax": st.column_config.NumberColumn("Tax", format="€%.2f"),
            "net_income": st.column_config.NumberColumn("Net dividend", format="€%.2f"),
            "currency": "Currency",
        },
    )