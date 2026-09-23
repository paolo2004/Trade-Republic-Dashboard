"""Tests for the average-cost position accounting in ``utils.metrics``.

These cover the numbers a user would check against their broker statement:
open shares, cost basis, average cost per share, and realised profit/loss.
"""

import pandas as pd
import pytest
from conftest import StreamlitStop, trade, trades_frame
from utils.metrics import calculate_positions, get_trades_transactions


def only_position(rows):
    """Run the accounting over one asset and return its single result row."""
    positions = calculate_positions(trades_frame(rows))
    assert len(positions) == 1
    return positions.iloc[0]


class TestSingleBuy:
    def test_cost_basis_includes_fees_and_taxes(self):
        position = only_position(
            [trade(shares=10, amount=-1000.0, fee=-1.0, tax=-0.5)]
        )

        assert position["open_shares"] == 10
        assert position["open_cost_basis"] == pytest.approx(1001.5)
        assert position["avg_cost_per_share"] == pytest.approx(100.15)
        assert position["total_purchase_cost"] == pytest.approx(1001.5)
        assert position["total_sale_proceeds"] == 0.0
        assert position["realised_profit_loss"] == 0.0

    def test_fee_and_tax_signs_do_not_matter(self):
        negative = only_position([trade(shares=10, amount=-1000.0, fee=-1.0, tax=-2.0)])
        positive = only_position([trade(shares=10, amount=-1000.0, fee=1.0, tax=2.0)])

        assert negative["open_cost_basis"] == positive["open_cost_basis"]
        assert negative["open_cost_basis"] == pytest.approx(1003.0)

    def test_share_count_sign_does_not_matter(self):
        position = only_position([trade(shares=-10, amount=-1000.0)])

        assert position["open_shares"] == 10


class TestMultipleBuys:
    def test_average_cost_blends_both_purchases(self):
        position = only_position(
            [
                trade(date="2024-01-01", shares=10, amount=-1000.0),
                trade(date="2024-02-01", shares=5, amount=-600.0, fee=-5.0),
            ]
        )

        assert position["open_shares"] == 15
        assert position["open_cost_basis"] == pytest.approx(1605.0)
        assert position["avg_cost_per_share"] == pytest.approx(107.0)


class TestPartialSell:
    def test_realised_profit_uses_the_average_cost_before_the_sale(self):
        position = only_position(
            [
                trade(date="2024-01-01", shares=10, amount=-1000.0),
                trade(
                    date="2024-02-01",
                    type="SELL",
                    shares=4,
                    amount=500.0,
                    fee=-1.0,
                    tax=-2.0,
                ),
            ]
        )

        # Average cost 100/share, so 4 shares remove 400 of cost basis.
        # Net proceeds are 500 - 3 = 497, giving 97 of realised profit.
        assert position["open_shares"] == pytest.approx(6)
        assert position["open_cost_basis"] == pytest.approx(600.0)
        assert position["avg_cost_per_share"] == pytest.approx(100.0)
        assert position["total_sale_proceeds"] == pytest.approx(497.0)
        assert position["realised_profit_loss"] == pytest.approx(97.0)

    def test_a_loss_is_reported_as_negative(self):
        position = only_position(
            [
                trade(date="2024-01-01", shares=10, amount=-1000.0),
                trade(date="2024-02-01", type="SELL", shares=5, amount=400.0),
            ]
        )

        assert position["realised_profit_loss"] == pytest.approx(-100.0)

    def test_selling_does_not_change_the_average_cost_per_share(self):
        position = only_position(
            [
                trade(date="2024-01-01", shares=10, amount=-1000.0, fee=-10.0),
                trade(date="2024-02-01", type="SELL", shares=5, amount=900.0),
            ]
        )

        assert position["avg_cost_per_share"] == pytest.approx(101.0)


class TestOversellAndShortSell:
    def test_selling_more_than_held_only_removes_the_shares_on_hand(self):
        # Ends with an open position so the result is readable; see the
        # zero-share case below for what a full exit currently does.
        position = only_position(
            [
                trade(date="2024-01-01", shares=5, amount=-500.0),
                trade(date="2024-02-01", type="SELL", shares=8, amount=800.0),
                trade(date="2024-03-01", shares=3, amount=-330.0),
            ]
        )

        assert position["open_shares"] == pytest.approx(3)
        assert position["open_cost_basis"] == pytest.approx(330.0)
        # Only the 5 shares actually held were matched against the sale.
        assert position["realised_profit_loss"] == pytest.approx(300.0)
        assert position["total_sale_proceeds"] == pytest.approx(800.0)

    def test_a_sale_without_holdings_books_proceeds_but_no_profit(self):
        position = only_position(
            [
                trade(date="2024-01-01", type="SELL", shares=2, amount=200.0),
                trade(date="2024-02-01", shares=4, amount=-400.0),
            ]
        )

        assert position["total_sale_proceeds"] == pytest.approx(200.0)
        assert position["realised_profit_loss"] == 0.0
        assert position["open_shares"] == pytest.approx(4)


class TestClosedPosition:
    def test_selling_out_completely_leaves_no_average_cost(self):
        position = only_position(
            [
                trade(date="2024-01-01", shares=10, amount=-1000.0, fee=-1.0),
                trade(
                    date="2024-02-01",
                    type="SELL",
                    shares=10,
                    amount=1200.0,
                    fee=-1.0,
                    tax=-2.0,
                ),
            ]
        )

        assert position["open_shares"] == 0.0
        assert position["open_cost_basis"] == 0.0
        assert pd.isna(position["avg_cost_per_share"])
        # Net proceeds 1197 against a cost basis of 1001.
        assert position["realised_profit_loss"] == pytest.approx(196.0)


class TestOrderingAndGrouping:
    def test_trades_are_processed_in_date_order_not_row_order(self):
        rows = [
            trade(
                date="2024-02-01", type="SELL", shares=4, amount=500.0, fee=-1.0, tax=-2.0
            ),
            trade(date="2024-01-01", shares=10, amount=-1000.0),
        ]
        out_of_order = calculate_positions(trades_frame(rows)).iloc[0]
        in_order = calculate_positions(trades_frame(rows[::-1])).iloc[0]

        assert out_of_order["realised_profit_loss"] == pytest.approx(97.0)
        assert out_of_order["realised_profit_loss"] == in_order["realised_profit_loss"]
        assert out_of_order["open_shares"] == in_order["open_shares"]

    def test_each_asset_gets_its_own_row(self, sample_trades):
        positions = calculate_positions(sample_trades)

        assert set(positions["name"]) == {"Asset A", "Asset B"}
        asset_a = positions.loc[positions["name"] == "Asset A"].iloc[0]
        assert asset_a["open_shares"] == 15
        assert asset_a["open_cost_basis"] == pytest.approx(1602.0)

    def test_identity_columns_are_carried_through(self, sample_trades):
        positions = calculate_positions(sample_trades)
        asset_b = positions.loc[positions["name"] == "Asset B"].iloc[0]

        assert asset_b["symbol"] == "US0000000002"
        assert asset_b["ticker"] == "BBB"
        assert asset_b["asset_class"] == "STOCK"

    def test_no_trades_produces_an_empty_frame(self):
        empty = trades_frame([trade()]).iloc[0:0]

        assert calculate_positions(empty).empty


class TestGetTradesTransactions:
    def test_keeps_only_buys_and_sells(self):
        frame = trades_frame(
            [
                trade(type="BUY"),
                trade(type="SELL", amount=100.0),
                trade(type="DIVIDEND", amount=5.0),
                trade(type="DEPOSIT", amount=500.0),
            ]
        )
        trades = get_trades_transactions(frame)

        assert trades["type"].tolist() == ["BUY", "SELL"]

    def test_returns_a_copy(self):
        frame = trades_frame([trade(type="BUY")])
        trades = get_trades_transactions(frame)
        trades.loc[trades.index[0], "amount"] = 999.0

        assert frame.loc[0, "amount"] == -100.0

    def test_stops_when_there_are_no_trades(self):
        frame = trades_frame([trade(type="DIVIDEND", amount=5.0)])

        with pytest.raises(StreamlitStop):
            get_trades_transactions(frame)
