import pytest
from unittest.mock import Mock
from networkx import Graph
from agentpy.objects import Object
from model.spaces.financial import BondMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_agentpy_object():
    # Assert
    assert issubclass(BondMarket, Object)


@pytest.fixture
def market():
    # Given
    model = Mock()
    market = BondMarket(model)
    market.setup()
    return market


def test_has_bonds_graph(market):
    # When
    market.setup()

    # Then
    assert isinstance(market.bonds, Graph)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def market_with_bonds():
    # Given
    bonds = Graph()
    model = Mock()
    market = BondMarket(model)
    market.setup()
    market.bonds = bonds
    return market, bonds


def test_add_issuer_creates_bonds_graph_node(market_with_bonds):
    # Given
    govt = Mock()
    market, bonds = market_with_bonds

    # When
    market.add_issuer(govt)

    # Then
    assert bonds.has_node(govt)
    assert bonds.nodes[govt]["role"] == "issuer"


def test_add_buyer_creates_bonds_graph_node(market_with_bonds):
    # Given
    agent = Mock()
    market, bonds = market_with_bonds

    # When
    market.add_buyer(agent)

    # Then
    assert bonds.has_node(agent)
    assert bonds.nodes[agent]["role"] == "buyer"


def test_get_issuers_returns_all_issuer_nodes(market_with_bonds):
    # Given
    issuer = Mock()
    market, bonds = market_with_bonds
    bonds.add_node(issuer, role="issuer")
    bonds.add_nodes_from([Mock() for _ in range(10)])

    # When
    result = market.get_issuers()

    # Then
    assert result == [issuer]


def test_get_issuer_bonds_returns_bonds_data(market_with_bonds):
    # Given
    issuer, buyer, other = Mock(), Mock(), Mock()
    market, bonds = market_with_bonds
    bonds.add_edge(issuer, buyer, principal=100, interests=5.0)
    bonds.add_edge(other, buyer, principal=200, interests=5.0)

    # When
    result = market.get_issuer_bonds(issuer)

    # Then
    assert len(result) == 1
    assert result[0]["buyer"] is buyer
    assert result[0]["principal"] == 100
    assert result[0]["interests"] == 5.0


def test_get_buyer_bonds_returns_bonds_data(market_with_bonds):
    # Given
    issuer, buyer, other = Mock(), Mock(), Mock()
    market, bonds = market_with_bonds
    bonds.add_edge(issuer, buyer, principal=100, interests=5.0)
    bonds.add_edge(issuer, other, principal=200, interests=5.0)

    # When
    result = market.get_buyer_bonds(buyer)

    # Then
    assert len(result) == 1
    assert result[0]["issuer"] is issuer
    assert result[0]["principal"] == 100
    assert result[0]["interests"] == 5.0


@pytest.fixture
def participants():
    govt = Mock()
    govt.reserves = 0
    govt.bond_supply = 0
    cb = govt.central_bank
    cb.reserves = 0
    bank = Mock()
    bank.reserves = 0
    return govt, bank, cb


@pytest.fixture
def market_with_participants(participants):
    # Given
    model = Mock()
    bonds = Graph()
    bonds.add_nodes_from(participants)
    market = BondMarket(model)
    market.setup()
    market.bonds = bonds
    return market, *participants


def test_buy_bonds_creates_bonds(market_with_participants):
    # Given
    market, govt, bank, cb = market_with_participants
    bonds = market.bonds

    # When
    market.buy_bonds(bank, govt, 500)
    market.buy_bonds(cb, govt, 500)

    # Then
    assert bonds.has_edge(govt, bank)
    assert bonds.has_edge(govt, cb)


def test_buy_bonds_reduces_bond_supply(market_with_participants):
    # Given
    market, govt, bank, cb = market_with_participants
    govt.bond_supply = 1200

    # When
    market.buy_bonds(bank, govt, 500)
    market.buy_bonds(cb, govt, 500)

    # Then
    assert govt.bond_supply == 200


def test_buy_bonds_increase_bonds_principal(market_with_participants):
    # Given
    market, govt, bank, cb = market_with_participants
    bonds = market.bonds

    # When
    market.buy_bonds(bank, govt, 500)
    market.buy_bonds(cb, govt, 500)

    # Then
    assert bonds[govt][bank]["principal"] == 500
    assert bonds[govt][cb]["principal"] == 500


def test_buy_bonds_increase_government_reserves(market_with_participants):
    # Given
    market, govt, bank, cb = market_with_participants

    # When
    market.buy_bonds(bank, govt, 500)
    market.buy_bonds(cb, govt, 500)

    # Then
    assert govt.reserves == 1000


def test_buy_bonds_decrease_bank_reserves(market_with_participants):
    # Given
    market, govt, bank, _ = market_with_participants
    bank.reserves = 700

    # When
    market.buy_bonds(bank, govt, 500)

    # Then
    assert bank.reserves == 200


def test_buy_bonds_increase_central_bank_reserves(market_with_participants):
    # Given
    market, govt, _, cb = market_with_participants
    cb.reserves = 200

    # When
    market.buy_bonds(cb, govt, 500)

    # Then
    assert cb.reserves == 700


def test_repay_bonds_repays_principal(market_with_participants):
    # Given
    market, govt, bank, cb = market_with_participants
    bonds = market.bonds
    bonds.add_edge(govt, bank, principal=200)
    bonds.add_edge(govt, cb, principal=300)

    # When
    market.repay_bonds(govt, bank, 200, 10.0)
    market.repay_bonds(govt, cb, 300, 15.0)

    # Then
    assert bonds[govt][bank]["principal"] == 0
    assert bonds[govt][cb]["principal"] == 0


def test_repay_bonds_pays_interests(market_with_participants):
    # Given
    market, govt, bank, cb = market_with_participants
    bonds = market.bonds
    bonds.add_edge(govt, bank, principal=200)
    bonds.add_edge(govt, cb, principal=300)

    # When
    market.repay_bonds(govt, bank, 200, 10.0)
    market.repay_bonds(govt, cb, 300, 15.0)

    # Then
    assert bonds[govt][bank]["interests"] == 10.0
    assert bonds[govt][cb]["interests"] == 15.0


def test_repay_bonds_decrease_governemnt_reserves(market_with_participants):
    # Given
    market, govt, bank, cb = market_with_participants
    bonds = market.bonds
    bonds.add_edge(govt, bank, principal=200)
    bonds.add_edge(govt, cb, principal=200)
    govt.reserves = 500

    # When
    market.repay_bonds(govt, bank, 200, 10.0)
    market.repay_bonds(govt, cb, 200, 10.0)

    # Then
    assert govt.reserves == pytest.approx(80.0)


def test_repay_bonds_increase_bank_reserves(market_with_participants):
    # Given
    market, govt, bank, _ = market_with_participants
    bonds = market.bonds
    bonds.add_edge(govt, bank, principal=200)
    bank.reserves = 40

    # When
    market.repay_bonds(govt, bank, 200, 10.0)

    # Then
    assert bank.reserves == pytest.approx(250.0)


def test_repay_bonds_decrease_central_bank_reserves(market_with_participants):
    # Given
    market, govt, _, cb = market_with_participants
    bonds = market.bonds
    bonds.add_edge(govt, cb, principal=200)
    cb.reserves = 250

    # When
    market.repay_bonds(govt, cb, 200, 10.0)

    # Then
    assert cb.reserves == pytest.approx(40.0)
