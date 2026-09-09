"""Tests for currency conversion and the sector/country allocation breakdowns."""

import numpy as np
import pandas as pd
import pytest
from utils import metrics
from utils.metrics import (
    add_country_column,
    add_sector_column,
    calculate_country_allocation,
    calculate_sector_allocation,
    convert_usd_to_eur,
    get_country_for_ticker,
    get_sector_for_ticker,
)


class TestConvertUsdToEur:
    def test_applies_the_exchange_rate(self):
        assert convert_usd_to_eur(100.0, 0.9) == pytest.approx(90.0)

    def test_accepts_numeric_strings(self):
        assert convert_usd_to_eur("100", "0.9") == pytest.approx(90.0)

    def test_missing_price_stays_missing(self):
        assert convert_usd_to_eur(None, 0.9) is None

    def test_missing_rate_produces_nan(self):
        assert np.isnan(convert_usd_to_eur(100.0, np.nan))


def allocation_frame(rows):
    """Build the per-asset frame the allocation page feeds to these helpers."""
    return pd.DataFrame(rows)


class TestSectorAllocation:
    def test_sums_by_sector_and_sorts_by_size(self):
        allocation = calculate_sector_allocation(
            allocation_frame(
                [
                    {"name": "A", "sector": "Software", "total_invested": 100.0},
                    {"name": "B", "sector": "Banks", "total_invested": 300.0},
                    {"name": "C", "sector": "Software", "total_invested": 100.0},
                ]
            )
        )

        assert allocation["sector"].tolist() == ["Banks", "Software"]
        assert allocation["amount"].tolist() == [300.0, 200.0]

    def test_percentages_are_shares_of_the_total(self):
        allocation = calculate_sector_allocation(
            allocation_frame(
                [
                    {"name": "A", "sector": "Software", "total_invested": 250.0},
                    {"name": "B", "sector": "Banks", "total_invested": 750.0},
                ]
            )
        )

        assert allocation["percentage"].tolist() == pytest.approx([75.0, 25.0])
        assert allocation["percentage"].sum() == pytest.approx(100.0)

    def test_counts_distinct_assets_per_sector(self):
        allocation = calculate_sector_allocation(
            allocation_frame(
                [
                    {"name": "A", "sector": "Software", "total_invested": 100.0},
                    {"name": "A", "sector": "Software", "total_invested": 100.0},
                    {"name": "B", "sector": "Software", "total_invested": 100.0},
                ]
            )
        )

        assert allocation.loc[0, "assets"] == 2

    def test_a_zero_total_does_not_divide_by_zero(self):
        allocation = calculate_sector_allocation(
            allocation_frame(
                [
                    {"name": "A", "sector": "Software", "total_invested": 0.0},
                    {"name": "B", "sector": "Banks", "total_invested": 0.0},
                ]
            )
        )

        assert (allocation["percentage"] == 0).all()


class TestCountryAllocation:
    def test_sums_by_country_and_sorts_by_size(self):
        allocation = calculate_country_allocation(
            allocation_frame(
                [
                    {"name": "A", "country": "Germany", "total_invested": 100.0},
                    {"name": "B", "country": "United States", "total_invested": 400.0},
                    {"name": "C", "country": "Germany", "total_invested": 100.0},
                ]
            )
        )

        assert allocation["country"].tolist() == ["United States", "Germany"]
        assert allocation["amount"].tolist() == [400.0, 200.0]
        assert allocation["percentage"].tolist() == pytest.approx([200 / 3, 100 / 3])

    def test_a_zero_total_does_not_divide_by_zero(self):
        allocation = calculate_country_allocation(
            allocation_frame([{"name": "A", "country": "Germany", "total_invested": 0.0}])
        )

        assert (allocation["percentage"] == 0).all()


class TestSectorLookup:
    def test_uses_the_industry_reported_by_yahoo_finance(self, monkeypatch):
        monkeypatch.setattr(
            metrics, "load_ticker_info", lambda ticker: {"industry": "Semiconductors"}
        )

        assert get_sector_for_ticker("NVDA", "STOCK") == "Semiconductors"

    def test_falls_back_to_the_asset_class(self, monkeypatch):
        monkeypatch.setattr(metrics, "load_ticker_info", lambda ticker: {})

        assert get_sector_for_ticker("XYZ", "etf") == "ETF"

    def test_falls_back_to_unknown_without_an_asset_class(self, monkeypatch):
        monkeypatch.setattr(metrics, "load_ticker_info", lambda ticker: {})

        assert get_sector_for_ticker("XYZ", "") == "Unknown"

    def test_no_ticker_skips_the_lookup(self, monkeypatch):
        def fail(ticker):
            raise AssertionError("should not look up a missing ticker")

        monkeypatch.setattr(metrics, "load_ticker_info", fail)

        assert get_sector_for_ticker(None, "STOCK") == "Unknown"

    def test_adds_a_sector_column_per_row(self, monkeypatch):
        monkeypatch.setattr(
            metrics, "load_ticker_info", lambda ticker: {"industry": f"sector-{ticker}"}
        )
        frame = allocation_frame(
            [
                {"name": "A", "ticker": "AAA", "asset_class": "STOCK"},
                {"name": "B", "ticker": "BBB", "asset_class": "STOCK"},
            ]
        )
        result = add_sector_column(frame)

        assert result["sector"].tolist() == ["sector-AAA", "sector-BBB"]
        assert "sector" not in frame.columns


class TestCountryLookup:
    @pytest.mark.parametrize("asset_class", ["ETF", "ETC", "ETN", "FUND", "CRYPTO"])
    def test_pooled_and_crypto_assets_are_global(self, asset_class, monkeypatch):
        def fail(ticker):
            raise AssertionError("should not need a network lookup")

        monkeypatch.setattr(metrics, "load_ticker_info", fail)

        assert get_country_for_ticker("XYZ", asset_class) == "Global"

    def test_stocks_use_the_country_from_yahoo_finance(self, monkeypatch):
        monkeypatch.setattr(
            metrics, "load_ticker_info", lambda ticker: {"country": "Germany"}
        )

        assert get_country_for_ticker("SAP.DE", "STOCK") == "Germany"

    def test_missing_country_is_unknown(self, monkeypatch):
        monkeypatch.setattr(metrics, "load_ticker_info", lambda ticker: {})

        assert get_country_for_ticker("SAP.DE", "STOCK") == "Unknown"

    def test_no_ticker_skips_the_lookup(self, monkeypatch):
        def fail(ticker):
            raise AssertionError("should not look up a missing ticker")

        monkeypatch.setattr(metrics, "load_ticker_info", fail)

        assert get_country_for_ticker("", "STOCK") == "Unknown"

    def test_adds_a_country_column_per_row(self, monkeypatch):
        monkeypatch.setattr(
            metrics, "load_ticker_info", lambda ticker: {"country": "Germany"}
        )
        frame = allocation_frame(
            [
                {"name": "A", "ticker": "AAA", "asset_class": "STOCK"},
                {"name": "B", "ticker": "BBB", "asset_class": "ETF"},
            ]
        )
        result = add_country_column(frame)

        assert result["country"].tolist() == ["Germany", "Global"]
        assert "country" not in frame.columns
