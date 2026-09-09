import numpy as np
import plotly.express as px
import streamlit as st
from utils.chart import CATEGORICAL, show_chart
from utils.import_data import check_if_data_loaded, validate_data
from utils.metrics import (
    add_country_column,
    add_sector_column,
    calculate_country_allocation,
    calculate_sector_allocation,
    get_trades_transactions,
)
from utils.styling import setup_page

setup_page("Portfolio Allocation", "🥧")

st.markdown(
    """
    <div class="header">
        <h1>Portfolio Allocation</h1>
        <p>
            How your invested capital is distributed across
            assets, asset classes, sectors and countries.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

check_if_data_loaded()
df = st.session_state["df"].copy()
validate_data(df)

trade_transactions = get_trades_transactions(df)

# Use a share-weighted price because buy orders can contain different quantities.
trade_transactions["trade_value"] = trade_transactions["price"] * trade_transactions["shares"]

st.markdown('<div class="section-label">ALLOCATION SUMMARY</div>', unsafe_allow_html=True)

cel1, cel2, cel3 = st.columns(3)
# Negated because buys are negative amounts in the export.
cel1.metric("Total invested", f"€{-trade_transactions['amount'].sum():,.2f}")
cel2.metric("Trade transactions", f"{len(trade_transactions):,}")
cel3.metric("Unique assets", f"{trade_transactions['name'].nunique():,}")

allocation_by_asset = trade_transactions.groupby(
    ["name", "asset_class", "ticker"],
    as_index=False,
).agg(
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

allocation_by_asset["total_invested"] = allocation_by_asset["total_invested"].abs()

with st.spinner("Resolving sectors and countries..."):
    allocation_by_asset = add_sector_column(allocation_by_asset)
    allocation_by_asset = add_country_column(allocation_by_asset)

sector_allocation = calculate_sector_allocation(allocation_by_asset)
country_allocation = calculate_country_allocation(allocation_by_asset)
sorted_allocation = allocation_by_asset.sort_values(by="total_invested", ascending=False)


def allocation_bar(data, value_column, label_column, value_title, height=350):
    """Sorted horizontal bar - the readable form for many close-valued shares."""
    figure = px.bar(
        data.sort_values(value_column, ascending=True),
        x=value_column,
        y=label_column,
        orientation="h",
        labels={label_column: "", value_column: value_title},
    )
    figure.update_traces(marker_color=CATEGORICAL[0])
    show_chart(figure, height=height)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### Portfolio allocation")
        st.caption("Invested capital per asset.")
        allocation_bar(sorted_allocation, "total_invested", "name", "Invested (€)")

with col2:
    with st.container(border=True):
        st.markdown("### Allocation by asset class")
        st.caption("A coarse split, so a donut still reads at a glance.")

        asset_class = df.groupby("asset_class")["amount"].sum().abs().reset_index()
        figure = px.pie(asset_class, names="asset_class", values="amount", hole=0.68)
        figure.update_traces(marker=dict(line=dict(color="#10151d", width=2)))
        show_chart(figure)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### Stock allocation")
        st.caption("Invested capital across your equity positions.")

        stock_allocation = sorted_allocation[sorted_allocation["asset_class"] == "STOCK"]
        if stock_allocation.empty:
            st.info("No stock transactions found.")
        else:
            allocation_bar(stock_allocation, "total_invested", "name", "Invested (€)")

with col2:
    with st.container(border=True):
        st.markdown("### Crypto allocation")
        st.caption("Invested capital across your crypto positions.")

        crypto_allocation = sorted_allocation[sorted_allocation["asset_class"] == "CRYPTO"]
        if crypto_allocation.empty:
            st.info("No crypto transactions found.")
        else:
            allocation_bar(crypto_allocation, "total_invested", "name", "Invested (€)")

columns = st.columns(2)

with columns[0]:
    with st.container(border=True):
        st.markdown("### Allocation by country")
        st.caption("Where your invested capital is domiciled.")

        country_figure = px.pie(
            country_allocation,
            values="amount",
            names="country",
            hole=0.68,
        )
        country_figure.update_traces(
            marker=dict(line=dict(color="#10151d", width=2)),
        )
        show_chart(country_figure)

with columns[1]:
    with st.container(border=True):
        st.markdown("### Allocation by sector")
        st.caption("Sectors ranked by invested capital.")
        allocation_bar(sector_allocation, "amount", "sector", "Invested (€)")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("### Allocation by asset")
        st.caption("Invested capital per asset, largest first.")

        display_columns = [
            "name",
            "total_invested",
            "total_shares",
            "number_of_trade_transactions",
            "sector",
            "country",
        ]
        st.dataframe(
            sorted_allocation[display_columns],
            width="stretch",
            hide_index=True,
            column_config={
                "name": st.column_config.TextColumn("Asset"),
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
                "sector": st.column_config.TextColumn("Sector"),
                "country": st.column_config.TextColumn("Country"),
            },
        )

with col2:
    with st.container(border=True):
        st.markdown("### Allocation over time")
        st.caption("Capital committed on each trading day.")

        allocation_over_time = trade_transactions.groupby("date", as_index=False).agg(
            total_invested=("amount", "sum")
        )
        allocation_over_time["total_invested"] = allocation_over_time["total_invested"].abs()

        figure = px.line(
            allocation_over_time,
            x="date",
            y="total_invested",
            labels={"date": "", "total_invested": "Invested (€)"},
        )
        figure.update_traces(line_width=2)
        show_chart(figure, height=400)

with st.expander("Show raw data"):
    st.dataframe(df, width="stretch", hide_index=True)
