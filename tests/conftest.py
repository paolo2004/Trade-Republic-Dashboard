"""Shared fixtures and helpers for the test suite.

The app modules import each other as ``utils.<module>``, so ``app`` is added to
pytest's ``pythonpath`` in pyproject.toml.
"""

import io
import socket

import pandas as pd
import pytest
import streamlit as st


class StreamlitStop(Exception):
    """Raised in place of ``st.stop()`` so guard clauses are observable in tests."""


@pytest.fixture(autouse=True)
def stop_raises(monkeypatch):
    """Make ``st.stop()`` raise instead of silently returning.

    Outside a Streamlit runtime ``st.stop()`` only logs a warning and returns,
    so guarded functions would keep running and return ``None``. Raising makes
    the guards assertable and stops a missed guard from producing confusing
    downstream failures.
    """

    def _stop():
        raise StreamlitStop

    monkeypatch.setattr(st, "stop", _stop)


@pytest.fixture(autouse=True)
def clear_streamlit_caches():
    """Reset ``st.cache_data`` caches so mocked lookups are not served stale."""
    st.cache_data.clear()
    yield
    st.cache_data.clear()


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Fail loudly if a test reaches OpenFIGI or Yahoo Finance for real.

    Every outbound call is meant to be mocked; a live call would make the suite
    slow, flaky, and dependent on market hours.
    """

    def blocked(*args, **kwargs):
        raise RuntimeError(
            "This test tried to open a network connection. "
            "Mock the OpenFIGI or Yahoo Finance call instead."
        )

    monkeypatch.setattr(socket, "socket", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)


class FakeUpload(io.BytesIO):
    """Stand-in for Streamlit's UploadedFile: bytes plus a ``name``."""

    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name


def trade(
    *,
    date="2024-01-01",
    type="BUY",
    name="Asset A",
    symbol="US0000000001",
    asset_class="STOCK",
    ticker="AAA",
    shares=1.0,
    amount=-100.0,
    fee=0.0,
    tax=0.0,
):
    """Build one transaction row with Trade Republic export sign conventions.

    ``amount`` is negative for buys and positive for sells; ``fee`` and ``tax``
    are negative. The production code takes absolute values, which the tests
    exercise explicitly.
    """
    return {
        "date": date,
        "type": type,
        "name": name,
        "symbol": symbol,
        "asset_class": asset_class,
        "ticker": ticker,
        "shares": shares,
        "amount": amount,
        "fee": fee,
        "tax": tax,
    }


def trades_frame(rows):
    """Build a trades DataFrame with a real datetime ``date`` column."""
    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["date"])
    return frame


@pytest.fixture
def sample_trades():
    """A small two-asset portfolio with buys only."""
    return trades_frame(
        [
            trade(date="2024-01-05", shares=10, amount=-1000.0, fee=-1.0),
            trade(date="2024-02-05", shares=5, amount=-600.0, fee=-1.0),
            trade(
                date="2024-01-20",
                name="Asset B",
                symbol="US0000000002",
                ticker="BBB",
                shares=2,
                amount=-400.0,
            ),
        ]
    )
