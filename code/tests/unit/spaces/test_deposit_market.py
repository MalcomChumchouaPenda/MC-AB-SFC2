import pytest
from unittest.mock import Mock
from networkx import Graph
from agentpy.objects import Object
from model.spaces.deposit_market import DepositMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_agentpy_object():
    # Assert
    assert issubclass(DepositMarket, Object)


@pytest.fixture
def market():
    # Given
    model = Mock()
    market = DepositMarket(model)
    market.setup()
    return market


def test_has_deposits_graph(market):
    # When
    market.setup()

    # Then
    assert isinstance(market.deposits, Graph)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def market_with_deposits():
    # Given
    deposits = Graph()
    model = Mock()
    market = DepositMarket(model)
    market.deposits = deposits
    return market, deposits


def test_add_client_creates_deposits_graph_node(market_with_deposits):
    # Given
    client = Mock()
    market, deposits = market_with_deposits

    # When
    market.add_client(client)

    # Then
    assert deposits.has_node(client)
    assert deposits.nodes[client]["role"] == "client"


def test_add_bank_creates_deposits_graph_node(market_with_deposits):
    # Given
    bank = Mock()
    market, deposits = market_with_deposits

    # When
    market.add_bank(bank)

    # Then
    assert deposits.has_node(bank)
    assert deposits.nodes[bank]["role"] == "bank"


def test_get_bank_deposits_returns_deposits_data(market_with_deposits):
    # Given
    bank, client, other = Mock(), Mock(), Mock()
    market, deposits = market_with_deposits
    deposits.add_edge(bank, client, amount=100, interests=5.0)
    deposits.add_edge(other, client, amount=200, interests=5.0)

    # When
    result = market.get_bank_deposits(bank)

    # Then
    assert len(result) == 1
    assert result[0]["client"] is client
    assert result[0]["amount"] == 100
    assert result[0]["interests"] == 5.0


def test_get_client_deposits_returns_deposits_data(market_with_deposits):
    # Given
    bank, client, other = Mock(), Mock(), Mock()
    market, deposits = market_with_deposits
    deposits.add_edge(bank, client, amount=100, interests=5.0)
    deposits.add_edge(bank, other, amount=200, interests=5.0)

    # When
    result = market.get_client_deposits(client)

    # Then
    assert len(result) == 1
    assert result[0]["bank"] is bank
    assert result[0]["amount"] == 100
    assert result[0]["interests"] == 5.0


def test_get_banks(market_with_deposits):
    # Given
    bank, other = Mock(), Mock()
    market, deposits = market_with_deposits
    deposits.add_node(bank, role="bank")
    deposits.add_node(other, role="client")

    # When
    sample = market.get_banks()

    # Then
    assert sample == [bank]


def test_get_defaulted_banks(market_with_deposits):
    # Given
    bank1 = Mock(defaulted=True)
    bank2 = Mock(defaulted=False)
    other = Mock()
    market, deposits = market_with_deposits
    deposits.add_node(bank1, role="bank")
    deposits.add_node(bank2, role="bank")
    deposits.add_node(other, role="client")

    # When
    sample = market.get_defaulted_banks()

    # Then
    assert sample == [bank1]


@pytest.fixture
def participants():
    client = Mock(cash=0)
    bank = Mock(reserves=0)
    return client, bank


@pytest.fixture
def market_with_participants(participants):
    # Given
    model = Mock()
    deposits = Graph()
    deposits.add_nodes_from(participants)
    market = DepositMarket(model)
    market.deposits = deposits
    return market, *participants


def test_open_account_creates_deposits(market_with_participants):
    # Given
    market, client, bank = market_with_participants
    deposits = market.deposits

    # When
    market.open_account(client, bank)

    # Then
    assert deposits.has_edge(client, bank)


def test_open_account_with_initial_amount(market_with_participants):
    # Given
    market, client, bank = market_with_participants
    deposits = market.deposits

    # When
    market.open_account(client, bank, amount=500)

    # Then
    assert deposits[client][bank]["amount"] == 500


def test_close_account_removes_deposits(market_with_participants):
    # Given
    market, client, bank = market_with_participants
    deposits = market.deposits
    deposits.add_edge(client, bank, amount=100)

    # When
    market.close_account(client, bank)

    # Then
    assert not deposits.has_edge(client, bank)


def test_close_account_transfers_cash(market_with_participants):
    # Given
    market, client, bank = market_with_participants
    deposits = market.deposits
    deposits.add_edge(client, bank, amount=100)

    # When
    market.close_account(client, bank)

    # Then
    assert client.cash == 100
    assert bank.reserves == -100


def test_close_account_return_deposit_amount(market_with_participants):
    # Given
    market, client, bank = market_with_participants
    deposits = market.deposits
    deposits.add_edge(client, bank, amount=200)

    # When
    amount = market.close_account(client, bank)

    # Then
    assert amount == 200


def test_pay_interests_increases_deposits_amount(market_with_participants):
    # Given
    market, client, bank = market_with_participants
    deposits = market.deposits
    deposits.add_edge(client, bank, amount=200)

    # When
    market.pay_interests(client, bank, 10.0)

    # Then
    assert deposits[client][bank]["amount"] == 210.0


def test_pay_interests_increases_deposits_interest(market_with_participants):
    # Given
    market, client, bank = market_with_participants
    deposits = market.deposits
    deposits.add_edge(client, bank, amount=200)

    # When
    market.pay_interests(client, bank, 10.0)

    # Then
    assert deposits[client][bank]["interests"] == 10.0


def test_make_deposits_increases_deposits_amount(market_with_participants):
    # Given
    market, client, bank = market_with_participants
    deposits = market.deposits
    deposits.add_edge(client, bank, amount=200)

    # When
    market.make_deposits(client, bank, 500)

    # Then
    assert deposits[client][bank]["amount"] == 700


def test_make_deposits_transfers_cash(market_with_participants):
    # Given
    market, client, bank = market_with_participants
    client.cash = 500
    deposits = market.deposits
    deposits.add_edge(client, bank, amount=0)

    # When
    market.make_deposits(client, bank, 500)

    # Then
    assert client.cash == 0
    assert bank.reserves == 500


def test_reimburse_deposits_decreases_deposits_amount(market_with_participants):
    # Given
    market, client, bank = market_with_participants
    govt = Mock(reserves=100)
    deposits = market.deposits
    deposits.add_edge(client, bank, amount=100, interests=10.0)

    # When
    market.reimburse_deposits(govt, client, bank)

    # Then
    assert deposits[client][bank]["amount"] == 0.0
    assert deposits[client][bank]["interests"] == 10.0


def test_reimburse_deposits_transfers_cash(market_with_participants):
    # Given
    market, client, bank = market_with_participants
    govt = Mock(reserves=200)
    deposits = market.deposits
    deposits.add_edge(client, bank, amount=100, interests=10.0)

    # When
    market.reimburse_deposits(govt, client, bank)

    # Then
    assert client.cash == 100
    assert govt.reserves == 100
