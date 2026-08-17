import pandas as pd
import streamlit as st
from utils.ticker_lookup import get_crypto_ticker, get_ticker_from_isin


def load_data(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith((".csv", ".txt")):
        df = pd.read_csv(
            uploaded_file,
            encoding="ISO-8859-1",
            sep=None,
            engine="python",
        )
    elif file_name.endswith((".xls", ".xlsx")):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file type")

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for column in ["amount", "fee", "tax", "price", "shares", "quantity", "fy_rate"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    if "month" not in df.columns and "date" in df.columns:
        df["month"] = df["date"].dt.to_period("M").astype(str)

    columns_to_drop = ["account_type", "counterparty_iban", "payment_reference", "mcc_code"]
    df = df.drop(columns=columns_to_drop, errors="ignore")

    if "symbol" in df.columns:
        is_crypto = (
            df.get("asset_class", pd.Series("", index=df.index))
            .astype(str)
            .str.strip()
            .str.upper()
            .eq("CRYPTO")
        )

        # Crypto tickers go directly into the shared `ticker` column.
        df["ticker"] = None
        df.loc[is_crypto, "ticker"] = df.loc[is_crypto].apply(
            get_crypto_ticker,
            axis=1,
        )

        # Only securities need the ISIN → ticker lookup.
        unique_isins = df.loc[~is_crypto, "symbol"].dropna().unique()

        with st.spinner("Looking up ticker symbols..."):
            isin_map = {isin: get_ticker_from_isin(isin) for isin in unique_isins}

        df.loc[~is_crypto, "ticker"] = df.loc[~is_crypto, "symbol"].map(isin_map)
    return df


def validate_data(df):
    required_columns = ["date", "type", "name", "shares", "amount", "currency"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    # Check for empty DataFrame
    if df.empty:
        raise ValueError("The uploaded file does not contain any rows.")

    # Check for valid date format
    try:
        pd.to_datetime(df["date"])
    except Exception as error:
        raise ValueError("Invalid date format in the 'date' column.") from error

    return True


def check_if_data_loaded():
    if "df" not in st.session_state:
        st.warning("Please upload a file on the main page first.")
        st.stop()
