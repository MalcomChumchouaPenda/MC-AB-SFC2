import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import DepositMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(DepositMarket, EcoSpace)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


class FakeRole:
    pass


@pytest.fixture
def market():
    # Given
    model = Mock()
    market = DepositMarket(model)
    return market


def test_add_deposit_holder_creates_deposit_holder_role(market, monkeypatch):
    # Given
    household = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.DepositHolderRole", FakeRole)

    # When
    deposit_holder = market.add_deposit_holder(household)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, household, "deposit_holder")
    assert deposit_holder is action.return_value


def test_add_deposit_bank_creates_deposit_bank(market, monkeypatch):
    # Given
    bank = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.DepositBankRole", FakeRole)

    # When
    deposit_bank = market.add_deposit_bank(bank)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, bank, "deposit_bank")
    assert deposit_bank is action.return_value


def test_assign_deposit_bank_by_adding_graph_edge(market):
    # Given
    deposit_holder = Mock()
    deposit_bank = Mock()
    market.graph.add_nodes_from([deposit_holder, deposit_bank])

    # When
    market.assign_deposit_bank(deposit_holder, deposit_bank)

    # Then
    edges = list(market.graph.edges)
    source, target = edges[0]
    assert len(edges) == 1
    assert source is deposit_holder
    assert target is deposit_bank
    assert deposit_holder.deposit_bank is deposit_bank
