import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px
from utils.analysis import format_number, format_large_number, format_percentage
from utils.ticker_lookup import _validate_yahoo_ticker

st.set_page_config(page_title="Asset Analysis", page_icon="📈")

st.title("📈 Asset Analysis")
st.markdown("Get real-time market information for any asset in your portfolio.")

# ============================================================
# LOAD PORTFOLIO DATA
# ============================================================

st.markdown("---")

df = st.session_state.get("df")


if df is None or df.empty:

    st.warning(
        "No portfolio data found. "
        "Please upload your Trade Republic file first."
    )

    st.stop()

assets = (df[["name", "symbol", "ticker"]].dropna(subset=["ticker"]).drop_duplicates().sort_values("name")) 

# ============================================================
# Get ticker symbol from user input or selected asset
# ============================================================

st.sidebar.header("Asset Lookup")
selected_asset = st.sidebar.selectbox("Select an asset from your portfolio", 
                                      options=assets["name"].tolist(),
                                        index=0) 
manual_ticker_input = st.sidebar.text_input("Or enter another Yahoo Finance ticker symbol (e.g., AAPL, MSFT, TSLA):", value="")

ticker_symbol = None
display_name = selected_asset

if manual_ticker_input:
    manual_ticker = manual_ticker_input.strip().upper()
    if _validate_yahoo_ticker(manual_ticker):
        ticker_symbol = manual_ticker
        display_name = manual_ticker
    else:
        st.sidebar.warning("Invalid ticker symbol. Please enter a valid Yahoo Finance ticker.")
else:
    ticker_symbol = assets.loc[assets["name"] == selected_asset, "ticker"].values[0] if selected_asset else None

period = st.sidebar.selectbox("Select period", options=["1M", "3M", "6M", "1Y", "2Y", "YTD", "Max"], index=5)
period = period.lower()

# ============================================================
# COMPANY INFORMATION
# ============================================================

ticker = yf.Ticker(ticker_symbol)
with st.spinner(f"Loading company information..."):
    try:
        info = ticker.info
    except Exception :
        info = {}

st.markdown(
    f"""
    ### {info.get('longName', selected_asset)} 

    Detailed market and financial information for this asset.
    """
)

with st.spinner(f"Fetching data for {info.get('longName')}..."):
    data = ticker.history(period=period)

if data.empty:
    st.warning(f"No market data found for {info.get('longName')} ({ticker_symbol}).")
    st.stop()

latest_price = data["Close"].iloc[-1]
previous_close = data["Close"].iloc[-2] if len(data) > 1 else latest_price
price_change = latest_price - previous_close
price_change_percent = (price_change / previous_close * 100) if previous_close != 0 else 0

# ============================================================
# PRICE METRICS
# ============================================================


col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Current Price",
              f"${format_number(latest_price, 2)}", 
              f"{price_change_percent:.2f}%" 
              if price_change_percent is not None else "None")

with col2:
    high_52 = data["Close"].max()
    st.metric("52 Week High", f"${format_number(high_52, 2)}")

with col3:
    low_52 = data["Close"].min()
    st.metric("52 Week Low", f"${format_number(low_52, 2)}")

with col4:
    volume = data["Volume"].iloc[-1]
    st.metric("Volume", f"{format_large_number(volume)}")

# ============================================================
# PRICE CHART
# ============================================================

st.markdown("---")

st.subheader(f"Price History for {info.get('longName')} ")
fig = px.line(
    data.reset_index(),
    x="Date",
    y="Close"
)
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Price",
    hovermode="x unified",
    height=500
)
st.plotly_chart(fig, use_container_width=True)


# ============================================================
# Basic INFORMATION
# ============================================================

st.subheader("🏢 Company Overview")

company_col1, company_col2 = st.columns(2)

with company_col1:
    st.write(
        f"**Company:** "
        f"{info.get('longName', selected_asset)}"
    )
    st.write(
        f"**Ticker:** "
        f"{ticker_symbol}"
    )
    st.write(
        f"**Sector:** "
        f"{info.get('sector', 'N/A')}"
    )
    st.write(
        f"**Industry:** "
        f"{info.get('industry', 'N/A')}"
    )

with company_col2:
    st.write(
        f"**Country:** "
        f"{info.get('country', 'N/A')}"
    )
    st.write(
        f"**Exchange:** "
        f"{info.get('exchange', 'N/A')}"
    )
    st.write(
        f"**Currency:** "
        f"{info.get('currency', 'N/A')}"
    )
    website = info.get("website")
    if website:

        st.write(
            f"**Website:** "
            f"[Visit website]({website})"
        )

st.markdown("---")

# ============================================================
# Valuation Metrics
# ============================================================

st.subheader("💰 Valuation")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Market Cap:", format_large_number(info.get('marketCap', 'N/A')))
with col2:
    st.metric("PE Ratio:", format_number(info.get('trailingPE', 'N/A')))
with col3:
    st.metric("Dividend Yield:", format_percentage(info.get('dividendYield', 'N/A')))
with col4:
    st.metric("Price/Book:", format_number(info.get('priceToBook', 'N/A')))

st.markdown("---")

# ============================================================
# Profitability
# ============================================================

st.subheader("📊 Profitability")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("ROE:", format_percentage(info.get('returnOnEquity', 'N/A')))
with col2:
    st.metric("ROA:", format_percentage(info.get('returnOnAssets', 'N/A')))
with col3:
    st.metric("Profit Margin:", format_percentage(info.get('profitMargins', 'N/A')))
with col4:
    st.metric("Operating Margin:", format_percentage(info.get('operatingMargins', 'N/A')))

st.markdown("---")

# ============================================================
# Growth 
# ============================================================

st.subheader("📈 Growth")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Revenue Growth:", format_percentage(info.get('revenueGrowth', 'N/A')))
with col2:
    st.metric("Earnings Growth:", format_percentage(info.get('earningsGrowth', 'N/A')))
with col3:
    st.metric("EPS:", format_number(info.get('trailingEps', 'N/A')))
with col4:
    st.metric("Forward EPS:", format_number(info.get('forwardEps', 'N/A')))

st.markdown("---")

# ============================================================
# Dividends 
# ============================================================

st.subheader("💵 Dividends")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Dividend Yield:", format_percentage(info.get('dividendYield', 'N/A')))
with col2:
    st.metric("Annual Dividend:", format_number(info.get('dividendRate', 'N/A')))
with col3:
    st.metric("Dividend Ratio:", format_percentage(info.get('payoutRatio', 'N/A')))
with col4:
    ex_dividend = info.get('exDividendDate')
    if ex_dividend:
        try:
            ex_dividend_date = pd.to_datetime(ex_dividend, unit='s').strftime('%Y-%m-%d')
        except :
            pass

    st.metric("Ex-Dividend Date:", ex_dividend_date if ex_dividend else "N/A")

st.markdown("---")

# ============================================================
# Company Description
# ============================================================

summary = info.get('longBusinessSummary')
if summary:
    st.subheader("📝 About the Company")
    st.write(summary)

st.markdown("---")

# ============================================================
# FINANCIAL STATEMENTS
# ============================================================

st.subheader("📑 Financial Statements")


statement_type = st.selectbox(
    "Select statement",
    [
        "Income Statement",
        "Balance Sheet",
        "Cash Flow"
    ]
)

try:

    if statement_type == "Income Statement":

        financial_statement = ticker.income_stmt

    elif statement_type == "Balance Sheet":

        financial_statement = ticker.balance_sheet

    else:

        financial_statement = ticker.cashflow


    if financial_statement is not None and not financial_statement.empty:

        st.dataframe(
            financial_statement,
            use_container_width=True
        )

    else:

        st.info(
            "Financial statement data is not available."
        )

except Exception:

    st.warning(
        "Could not load financial statements."
    )
