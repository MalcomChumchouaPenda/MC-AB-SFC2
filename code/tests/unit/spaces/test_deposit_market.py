from unittest.mock import Mock
from dataclasses import dataclass
import pytest
from networkx import DiGraph
from mc_ab_sfc.spaces import DepositMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(DepositMarket, EcoSpace)


def test_has_directed_graph():
    # Given
    model = Mock()
    market = DepositMarket(model)

    # Assert
    assert isinstance(market.graph, DiGraph)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@dataclass(frozen=True)
class FakeEntityRole:
    owner: object = None
    space: object = None
    label: int = 2


@dataclass(frozen=True)
class FakeDepositorRole:
    owner: object = None
    space: object = None
    label: int = 2


@pytest.fixture
def market(monkeypatch):
    # Given a market and fake role class
    model = Mock()
    market = DepositMarket(model)
    monkeypatch.setattr("mc_ab_sfc.spaces.DepositorRole", FakeDepositorRole)
    monkeypatch.setattr("mc_ab_sfc.spaces.DepositEntityRole", FakeEntityRole)
    return market


def test_add_depositor_creates_and_registers_depositor_role(market):
    # Given
    household = Mock(id=1, roles={})

    # When
    depositor = market.add_depositor(household)

    # Then
    assert isinstance(depositor, FakeDepositorRole)
    assert depositor.owner is household
    assert depositor.space is market
    assert depositor in market.nodes
    assert depositor is household.roles["depositor"]


def test_add_bank_creates_and_registers_deposit_entity_role(market):
    # Given
    bank = Mock(id=1, roles={})

    # When
    bank_role = market.add_bank(bank)

    # Then
    assert isinstance(bank_role, FakeEntityRole)
    assert bank_role.owner is bank
    assert bank_role.space is market
    assert bank_role in market.nodes
    assert bank_role is bank.roles["deposit_entity"]


def test_assign_bank_by_adding_graph_edge(market):
    # Given
    depositor = Mock(label=1)
    bank_role = Mock(label=2)
    market.graph.add_nodes_from([depositor, bank_role])

    # When
    market.assign_bank(depositor, bank_role)

    # Then
    edges = list(market.graph.edges)
    source, target = edges[0]
    assert len(edges) == 1
    assert source is depositor
    assert target is bank_role
    assert depositor.bank is bank_role
