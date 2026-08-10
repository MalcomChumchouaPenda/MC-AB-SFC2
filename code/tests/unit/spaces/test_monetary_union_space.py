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


def test_contains_countries():
    # Given
    model = Mock()
    union = MonetaryUnionSpace(model)

    # Assert
    assert hasattr(union, "countries")
    assert isinstance(union.countries, dict)


def test_contains_international_markets():
    # Given
    model = Mock()
    union = MonetaryUnionSpace(model)

    # Assert
    assert hasattr(union, "markets")
    assert isinstance(union.markets, dict)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def monetary_union():
    # Given
    model = Mock()
    return MonetaryUnionSpace(model)


class FakeRole:
    pass


def test_add_commercial_bank_creates_commercial_bank_role(monetary_union, monkeypatch):
    # Given
    agent = Mock()
    monetary_union.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.CommercialBankRole", FakeRole)

    # When
    commercial_bank = monetary_union.add_commercial_bank(agent)

    # Then
    action = monetary_union.add_role
    action.assert_called_with(FakeRole, agent, "commercial_bank")
    assert commercial_bank is action.return_value


def test_add_central_bank_creates_central_bank_role(monetary_union, monkeypatch):
    # Given
    agent = Mock()
    monetary_union.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.CentralBankRole", FakeRole)

    # When
    central_bank = monetary_union.add_central_bank(agent)

    # Then
    action = monetary_union.add_role
    action.assert_called_with(FakeRole, agent, "central_bank")
    assert central_bank is action.return_value


def test_assign_central_bank_add_edge(monetary_union):
    # Given
    bank_role = Mock()
    central_role = Mock()
    graph = monetary_union.graph
    graph.add_nodes_from([bank_role, central_role])

    # When
    monetary_union.assign_central_bank(bank_role, central_role)

    # Then
    assert len(graph.edges) == 1
    assert graph.has_edge(central_role, bank_role)
    assert bank_role.central_bank is central_role


def test_request_cash_advances(monetary_union):
    # Given
    bank_role = Mock()
    central_role = Mock()
    graph = monetary_union.graph
    graph.add_nodes_from([bank_role, central_role])

    # When
    monetary_union.request_cash_advances(bank_role, central_role, 500)

    # Then
    bank_role.increase_stock.assert_any_call("reserves", 500)
    bank_role.increase_stock.assert_any_call("cash_advances", 500)
    central_role.increase_stock.assert_any_call("reserves", 500)
    central_role.increase_stock.assert_any_call("cash_advances", 500)
