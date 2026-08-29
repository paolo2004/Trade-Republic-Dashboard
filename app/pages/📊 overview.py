import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.import_data import check_if_data_loaded, validate_data
from utils.metrics import calculate_positions, get_current_prices, get_trades_transactions

st.set_page_config(
    page_title="Portfolio Overview",
    page_icon="💼",
    layout="wide",
)

st.title("💼 Portfolio Overview")
st.caption("Open positions, realised gains, income, and current portfolio value.")


# Load and normalise the exported transactions.
check_if_data_loaded()
df = st.session_state["df"].copy()
validate_data(df)

df = df.dropna(subset=["date"]).copy()

trade_transactions = get_trades_transactions(df)

# The selected period controls income and cash-flow charts. Positions use all
# history so that buys before the selected period remain part of open holdings.
latest_date = df["date"].max()
period_options = ("YTD", "6M", "1Y", "2Y", "All")
selected_period = st.selectbox("Analysis period", period_options)

if selected_period == "YTD":
    period_start = pd.Timestamp(year=latest_date.year, month=1, day=1)
elif selected_period == "6M":
    period_start = latest_date - pd.DateOffset(months=6)
elif selected_period == "1Y":
    period_start = latest_date - pd.DateOffset(years=1)
elif selected_period == "2Y":
    period_start = latest_date - pd.DateOffset(years=2)
else:
    period_start = df["date"].min()

period_df = df[df["date"] >= period_start].copy()


# Calculate holdings with average-cost accounting. Sells reduce the open share
# count and cost basis, while their gain/loss is recorded as realised P/L.
all_positions = calculate_positions(trade_transactions)

open_positions = all_positions[all_positions["open_shares"] > 1e-10].copy()

if open_positions.empty:
    st.info(
        "There are no open positions after accounting for sell orders."
    )
    st.stop()

tickers = tuple(open_positions["ticker"].dropna().loc[lambda values: values != ""].unique())

with st.spinner("Fetching current market prices..."):
    current_prices = get_current_prices(tickers)

open_positions["current_price"] = open_positions["ticker"].map(current_prices)
open_positions["market_value"] = (
    open_positions["open_shares"] * open_positions["current_price"]
)
open_positions["unrealised_profit_loss"] = (
    open_positions["market_value"] - open_positions["open_cost_basis"]
)
open_positions["unrealised_return_pct"] = np.where(
    open_positions["open_cost_basis"] > 0,
    open_positions["unrealised_profit_loss"] / open_positions["open_cost_basis"] * 100,
    np.nan,
)

# Amount is the gross payment in the Trade Republic export; fees and taxes are
# negative values, so adding them produces the net received income.
income_transactions = period_df[period_df["type"].isin(["DIVIDEND", "INTEREST_PAYMENT"])].copy()
income_transactions["net_income"] = (
    income_transactions["amount"] + income_transactions["fee"] + income_transactions["tax"]
)

net_dividends = income_transactions.loc[
    income_transactions["type"] == "DIVIDEND", "net_income"
].sum()
net_interest = income_transactions.loc[
    income_transactions["type"] == "INTEREST_PAYMENT", "net_income"
].sum()

period_income = net_dividends + net_interest

portfolio_value = open_positions["market_value"].sum(min_count=1)
open_cost_basis = open_positions["open_cost_basis"].sum()
unrealised_profit_loss = open_positions["unrealised_profit_loss"].sum(min_count=1)
realised_profit_loss = all_positions["realised_profit_loss"].sum()
total_profit_loss = unrealised_profit_loss + realised_profit_loss + period_income
cash_value = df[["amount", "fee", "tax"]].sum().sum()
total_return_pct = total_profit_loss / open_cost_basis * 100 if open_cost_basis > 0 else np.nan

# Portfolio summary
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Portfolio value", f"€{portfolio_value:,.2f}")
col2.metric(
    "Unrealised P/L",
    f"€{unrealised_profit_loss:,.2f}",
    f"{unrealised_profit_loss / open_cost_basis * 100:.2f}%" if open_cost_basis > 0 else None,
)
col3.metric("Realised P/L", f"€{realised_profit_loss:,.2f}")
col4.metric(
    "Total P/L",
    f"€{total_profit_loss:,.2f}",
    f"{total_return_pct:.2f}%" if pd.notna(total_return_pct) else None,
)
col5.metric("Cash", f"€{cash_value:,.2f}")
# col5.metric("Period Income", f"€{period_income:,.2f}")


# Open positions table
st.subheader("Open positions")

display_columns = [
    "name",
    "asset_class",
    "open_shares",
    "avg_cost_per_share",
    "current_price",
    "open_cost_basis",
    "market_value",
    "unrealised_profit_loss",
    "unrealised_return_pct",
    "realised_profit_loss",
]

position_table = open_positions[display_columns].sort_values("market_value", ascending=False)

st.dataframe(
    position_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "name": "Asset",
        "asset_class": "Asset class",
        "open_shares": st.column_config.NumberColumn("Open shares", format="%.2f"),
        "avg_cost_per_share": st.column_config.NumberColumn("Average cost/share", format="€%.2f"),
        "current_price": st.column_config.NumberColumn("Current price", format="€%.2f"),
        "open_cost_basis": st.column_config.NumberColumn("Open cost basis", format="€%.2f"),
        "market_value": st.column_config.NumberColumn("Market value", format="€%.2f"),
        "unrealised_profit_loss": st.column_config.NumberColumn("Unrealised P/L", format="€%.2f"),
        "unrealised_return_pct": st.column_config.NumberColumn(
            "Unrealised return", format="%.2f%%"
        ),
        "realised_profit_loss": st.column_config.NumberColumn("Realised P/L", format="€%.2f"),
    },
)

if open_positions["current_price"].isna().any():
    missing_prices = open_positions.loc[
        open_positions["current_price"].isna(), "name"
    ].tolist()
    st.warning("No current Yahoo Finance price was found for: " + ", ".join(missing_prices))


# Charts
left_column, right_column = st.columns(2)

with left_column:
    st.subheader("Profit / loss by asset")

    pnl_by_asset = open_positions.copy()
    pnl_by_asset["total_profit_loss"] = (
        pnl_by_asset["unrealised_profit_loss"] + pnl_by_asset["realised_profit_loss"]
    )

    pnl_by_asset = pnl_by_asset.sort_values("total_profit_loss")

    figure = px.bar(
        pnl_by_asset,
        x="total_profit_loss",
        y="name",
        orientation="h",
        color="total_profit_loss",
        color_continuous_scale=["#d62728", "#f7f7f7", "#2ca02c"],
        labels={
            "name": "",
            "total_profit_loss": "Profit / loss (€)",
        },
    )

    figure.update_traces(hovertemplate="%{y}<br>total_profit_loss: €%{x:,.2f}<extra></extra>")

    figure.update_xaxes(
        tickprefix="€",
        tickformat=",.2f",
    )

    st.plotly_chart(figure, use_container_width=True)

with right_column:
    st.subheader("Unrealised profit/loss by asset")
    performance = open_positions.dropna(subset=["unrealised_profit_loss"]).sort_values(
        "unrealised_profit_loss"
    )

    figure = px.bar(
        performance,
        x="unrealised_profit_loss",
        y="name",
        orientation="h",
        color="unrealised_profit_loss",
        color_continuous_scale=["#d62728", "#f7f7f7", "#2ca02c"],
        labels={"unrealised_profit_loss": "Unrealised P/L (€)", "name": ""},
    )

    figure.update_traces(hovertemplate="%{y}<br>Unrealised P/L: €%{x:,.2f}<extra></extra>")

    figure.update_xaxes(
        tickprefix="€",
        tickformat=",.2f",
    )

    st.plotly_chart(figure, use_container_width=True)


# Cash-flow and income during the selected period
chart_left, chart_right = st.columns(2)

with chart_left:
    st.subheader("Net investment cash flow")
    investment_flow = period_df[period_df["type"].isin(["BUY", "SELL"])].copy()
    investment_flow["net_cash_flow"] = (
        investment_flow["amount"] + investment_flow["fee"] + investment_flow["tax"]
    )
    investment_flow["month"] = investment_flow["date"].dt.to_period("M").astype(str)
    monthly_cash_flow = investment_flow.groupby("month", as_index=False)["net_cash_flow"].sum()

    figure = px.bar(
        monthly_cash_flow,
        x="month",
        y="net_cash_flow",
        labels={"month": "", "net_cash_flow": "Net cash flow (€)"},
    )
    st.plotly_chart(figure, use_container_width=True)

with chart_right:
    st.subheader("Passive income")
    passive_income = income_transactions[
        income_transactions["type"].isin(["DIVIDEND", "INTEREST_PAYMENT"])
    ].copy()

    if passive_income.empty:
        st.info("No dividends or interest payments in the selected period.")
    else:
        monthly_income = passive_income.groupby(["month", "type"], as_index=False)[
            "net_income"
        ].sum()

        figure = px.bar(
            monthly_income,
            x="month",
            y="net_income",
            color="type",
            barmode="group",
            labels={"month": "", "net_income": "Net income (€)", "type": ""},
        )
        st.plotly_chart(figure, use_container_width=True)


with st.expander("Income details"):
    income_summary = pd.DataFrame(
        {
            "Metric": [
                "Net dividends",
                "Net interest",
                "Total income",
            ],
            "Amount (€)": [
                net_dividends,
                net_interest,
                period_income,
            ],
        }
    )
    st.dataframe(income_summary, use_container_width=True, hide_index=True)


