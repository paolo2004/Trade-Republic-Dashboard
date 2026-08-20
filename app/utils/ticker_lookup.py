import requests
import streamlit as st
import yfinance as yf

OPENFIGI_URL = "https://api.openfigi.com/v3/mapping"
EXCHANGE_SUFFIXES = {
    "IR": "IR",
    "L": "L",
    "DE": "DE",
    "XET": "DE",
    "PA": "PA",
    "FP": "PA",
    "EP": "PA",
    "SW": "SW",
    "AS": "AS",
    "MI": "MI",
    "MC": "MC",
    "OL": "OL",
    "ST": "ST",
    "TO": "TO",
    "AX": "AX",
    "HK": "HK",
    "TW": "TW",
    "BR": "SA",
    "CN": "SS",
    "US": "",
}


def _format_yahoo_symbol(ticker, exch_code):
    """Convert an OpenFIGI ticker into a possible Yahoo Finance symbol."""

    if not ticker:
        return None

    ticker = str(ticker).strip().upper()

    if not ticker:
        return None

    exch_code = str(exch_code or "").strip().upper()

    suffix = EXCHANGE_SUFFIXES.get(exch_code)

    if suffix is None:
        return ticker

    if suffix == "":
        return ticker

    return f"{ticker}.{suffix}"


def _validate_yahoo_ticker(symbol):
    """Check whether a symbol exists on Yahoo Finance."""

    if not symbol:
        return False

    try:
        history = yf.Ticker(symbol).history(
            period="5d",
            raise_errors=False
        )

        return not history.empty

    except Exception:
        return False

@st.cache_data(show_spinner=False)
def get_ticker_from_isin(isin):
    """
    Convert an ISIN into a Yahoo Finance ticker.
    """

    if not isin:
        return None

    isin = isin.strip().upper()
    if not isin:
        return None

    headers = {
        "Content-Type": "application/json"
    }

    payload = [
        {
            "idType": "ID_ISIN",
            "idValue": isin,
        }
    ]

    try:
        response = requests.post(
            OPENFIGI_URL,
            json=payload,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or not data:
            return None

        row = data[0]
        candidates = []

        for item in row.get("data", []):
            ticker = item.get("ticker")
            exch_code = item.get("exchCode")
            if ticker and exch_code:
                candidates.append({"ticker": ticker, "exchCode": exch_code})

        #st.write(candidates)

        if not candidates:
            return None

        for candidate in candidates:
            symbol = _format_yahoo_symbol(candidate["ticker"], candidate["exchCode"])
            if _validate_yahoo_ticker(symbol):
                return symbol

        for candidate in candidates:
            ticker = candidate.get("ticker")

            if _validate_yahoo_ticker(ticker):
                return ticker

        return None
    except requests.exceptions.RequestException:
        return None
    except Exception:
        return None

def get_crypto_ticker(row):
    asset_class = str(row.get("asset_class", "")).strip().upper()
    symbol = str(row.get("symbol", "")).strip().upper()

    if asset_class != "CRYPTO" or not symbol:
        return None

    return f"{symbol}-USD"