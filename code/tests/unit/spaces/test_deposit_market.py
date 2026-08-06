
import pytest
from unittest.mock import Mock
from dataclasses import dataclass
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


@dataclass(frozen=True)
class FakeProviderRole:
    owner: object = None
    space: object = None
    label: int = 2


@dataclass(frozen=True)
class FakeHolderRole:
    owner: object = None
    space: object = None
    label: int = 2


@pytest.fixture
def market(monkeypatch):
    # Given a market and fake role class
    model = Mock()
    market = DepositMarket(model)
    monkeypatch.setattr("mc_ab_sfc.spaces.DepositHolderRole", FakeHolderRole)
    monkeypatch.setattr("mc_ab_sfc.spaces.DepositBankRole", FakeProviderRole)
    return market


def test_add_client_creates_and_registers_deposit_holder_role(market):
    # Given
    household = Mock(id=1, roles={})

    # When
    deposit_holder = market.add_client(household)

    # Then
    assert isinstance(deposit_holder, FakeHolderRole)
    assert deposit_holder.owner is household
    assert deposit_holder.space is market
    assert deposit_holder is household.roles["deposit_holder"]


def test_add_deposit_bank_creates_and_registers_deposit_deposit_bank(market):
    # Given
    bank = Mock(id=1, roles={})

    # When
    deposit_bank = market.add_deposit_bank(bank)

    # Then
    assert isinstance(deposit_bank, FakeProviderRole)
    assert deposit_bank.owner is bank
    assert deposit_bank.space is market
    assert deposit_bank is bank.roles["deposit_bank"]


def test_assign_deposit_bank_by_adding_graph_edge(market):
    # Given
    deposit_holder = Mock(label=1)
    deposit_bank = Mock(label=2)
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
