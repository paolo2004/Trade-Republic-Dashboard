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
    if not ticker:
        return None
    ticker = ticker.strip().upper()
    if not ticker:
        return None
    suffix = EXCHANGE_SUFFIXES.get((exch_code or "").upper())
    if suffix is None:
        return ticker
    if suffix == "":
        return ticker
    return f"{ticker}.{suffix}"


def _validate_yahoo_ticker(symbol):
    if not symbol:
        return False

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if info and info.get("regularMarketPrice") is not None:
            return True
        hist = ticker.history(period="1d")
        return not hist.empty
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

    headers = {"Content-Type": "application/json"}

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

        # st.write(candidates)

        if not candidates:
            return None

        for candidate in candidates:
            symbol = _format_yahoo_symbol(candidate["ticker"], candidate["exchCode"])
            if _validate_yahoo_ticker(symbol):
                return symbol

        for candidate in candidates:
            if _validate_yahoo_ticker(candidate["ticker"]):
                return candidate["ticker"]

        return _format_yahoo_symbol(candidates[0]["ticker"], candidates[0].get("exchCode"))
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
