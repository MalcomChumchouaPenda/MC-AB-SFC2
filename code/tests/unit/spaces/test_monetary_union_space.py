import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import MonetaryUnionSpace

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(MonetaryUnionSpace, EcoSpace)


def test_requires_model_and_central_bank():
    # Assert
    expected = "required positional arguments: 'model' and 'central_bank'"
    with pytest.raises(TypeError, match=expected):
        MonetaryUnionSpace()


class FakeRole:
    pass


def test_creates_and_registers_central_bank_role(monkeypatch):
    # Given
    model, central_bank, central_role = Mock(), Mock(), Mock()
    monkeypatch.setattr(MonetaryUnionSpace, "add_role", Mock(return_value=central_role))
    monkeypatch.setattr("mc_ab_sfc.spaces.CentralBankRole", FakeRole)

    # When
    union = MonetaryUnionSpace(model, central_bank)

    # Then
    union.add_role.assert_called_with(FakeRole, central_bank, "central_bank")
    assert union.central_bank_role is central_role


@pytest.fixture
def union(monkeypatch):
    # Given
    model, central_bank, central_role = Mock(), Mock(), Mock()
    monkeypatch.setattr(MonetaryUnionSpace, "add_role", Mock(return_value=central_role))
    monkeypatch.setattr("mc_ab_sfc.spaces.CentralBankRole", FakeRole)
    return MonetaryUnionSpace(model, central_bank)


def test_contains_countries(union):
    # Assert
    assert hasattr(union, "countries")
    assert isinstance(union.countries, dict)


def test_contains_international_markets(union):
    # Assert
    assert hasattr(union, "markets")
    assert isinstance(union.markets, dict)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_add_commercial_bank_creates_commercial_bank_role(union, monkeypatch):
    # Given
    agent = Mock()
    union.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.CommercialBankRole", FakeRole)

    # When
    commercial_bank = union.add_commercial_bank(agent)

    # Then
    action = union.add_role
    action.assert_called_with(FakeRole, agent, "commercial_bank")
    assert commercial_bank is action.return_value


def test_add_commercial_bank_creates_edge_with_central_role(union, monkeypatch):
    # Given
    bank_role, agent = Mock(), Mock()
    union.add_role = Mock(return_value=bank_role)
    monkeypatch.setattr("mc_ab_sfc.spaces.TaxPayerRole", FakeRole)
    central_role = union.central_bank_role
    graph = union.graph

    # When
    union.add_commercial_bank(agent)

    # Then
    assert len(graph.edges) == 1
    assert graph.has_edge(central_role, bank_role)
    assert bank_role.central_bank is central_role


def test_request_cash_advances(union):
    # Given
    bank_role = Mock()
    central_role = union.central_bank_role
    union.graph.add_nodes_from([bank_role, central_role])

    # When
    union.request_cash_advances(bank_role, central_role, 500)

    # Then
    bank_role.increase_stock.assert_any_call("reserves", 500)
    bank_role.increase_stock.assert_any_call("cash_advances", 500)
    central_role.increase_stock.assert_any_call("reserves", 500)
    central_role.increase_stock.assert_any_call("cash_advances", 500)
