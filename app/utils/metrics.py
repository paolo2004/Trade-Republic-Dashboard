import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf


def get_buy_transactions(df):
    buy_transactions = df[df["type"] == "BUY"].copy()
    if buy_transactions.empty:
        st.info("No buy transactions found. Allocation cannot be calculated.")
        st.stop()
    else:
        return buy_transactions


@st.cache_data(ttl=900, show_spinner=False)
def get_current_prices(tickers):
    """Return latest available Yahoo Finance prices, cached for 15 minutes."""
    prices = {}

    for ticker in tickers:
        if not ticker:
            continue

        try:
            yahoo_ticker = yf.Ticker(ticker)
            price = yahoo_ticker.fast_info.get("last_price")

            # Fallback: latest daily closing price if live data is unavailable.
            if price is None or pd.isna(price):
                history = yahoo_ticker.history(period="5d", auto_adjust=False)
                if not history.empty:
                    price = history["Close"].dropna().iloc[-1]

            prices[ticker] = float(price) if price is not None else np.nan

        except Exception:
            prices[ticker] = np.nan

    return prices


def calculate_positions(trades):
    """
    Calculate current positions and realised P/L using average-cost accounting.

    Buy:
        adds shares and purchase cost (trade amount + fees + taxes)

    Sell:
        reduces open shares and removes the proportional average cost basis.
        realised P/L = net sale proceeds - removed cost basis
    """
    positions = []

    group_columns = ["name", "symbol", "asset_class", "ticker"]

    for asset, asset_trades in trades.groupby(group_columns, dropna=False):
        name, symbol, asset_class, ticker = asset
        asset_trades = asset_trades.sort_values("date")

        open_shares = 0.0
        open_cost_basis = 0.0
        realised_profit_loss = 0.0
        total_purchase_cost = 0.0
        total_sale_proceeds = 0.0

        for _, trade in asset_trades.iterrows():
            shares = abs(trade["shares"])
            fees_and_taxes = abs(trade["fee"]) + abs(trade["tax"])

            if trade["type"] == "BUY":
                # `amount` is negative for buys in this export.
                purchase_cost = abs(trade["amount"]) + fees_and_taxes

                open_shares += shares
                open_cost_basis += purchase_cost
                total_purchase_cost += purchase_cost

            elif trade["type"] == "SELL":
                # `amount` is positive for sells; fees and taxes are negative.
                net_sale_proceeds = abs(trade["amount"]) - fees_and_taxes
                total_sale_proceeds += net_sale_proceeds

                if open_shares <= 0:
                    continue

                # Protect against an export containing a sale larger than holdings.
                shares_sold = min(shares, open_shares)

                average_cost_before_sale = open_cost_basis / open_shares
                removed_cost_basis = shares_sold * average_cost_before_sale

                open_shares -= shares_sold
                open_cost_basis -= removed_cost_basis
                realised_profit_loss += net_sale_proceeds - removed_cost_basis

        # Do not display assets that were fully sold.
        if open_shares > 1e-10:
            positions.append(
                {
                    "name": name,
                    "symbol": symbol,
                    "asset_class": asset_class,
                    "ticker": ticker,
                    "open_shares": open_shares,
                    "open_cost_basis": open_cost_basis,
                    "avg_cost_per_share": open_cost_basis / open_shares,
                    "total_purchase_cost": total_purchase_cost,
                    "total_sale_proceeds": total_sale_proceeds,
                    "realised_profit_loss": realised_profit_loss,
                }
            )

    return pd.DataFrame(positions)
