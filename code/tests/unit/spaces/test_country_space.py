import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import CountrySpace

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(CountrySpace, EcoSpace)


@pytest.fixture
def country():
    # Given
    model = Mock()
    space = CountrySpace(model)
    return space


def test_contains_local_markets(country):
    # Assert
    assert hasattr(country, "markets")
    assert isinstance(country.markets, dict)


def test_has_default_tax_rate(country):
    # Assert
    assert country.tax_rate == 0


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


class FakeRole:
    pass


def test_add_citizen_creates_citizen_role(country, monkeypatch):
    # Given
    household = Mock()
    country.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.CitizenRole", FakeRole)

    # When
    citizen = country.add_citizen(household)

    # Then
    action = country.add_role
    action.assert_called_with(FakeRole, household, "citizen")
    assert citizen is action.return_value


def test_add_tax_payer_creates_tax_payer_role(country, monkeypatch):
    # Given
    agent = Mock()
    country.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.TaxPayerRole", FakeRole)

    # When
    tax_payer = country.add_tax_payer(agent)

    # Then
    action = country.add_role
    action.assert_called_with(FakeRole, agent, "tax_payer")
    assert tax_payer is action.return_value


def test_add_government_creates_government_role(country, monkeypatch):
    # Given
    agent = Mock()
    country.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.GovernmentRole", FakeRole)

    # When
    govt_role = country.add_government(agent)

    # Then
    action = country.add_role
    action.assert_called_with(FakeRole, agent, "government")
    assert govt_role is action.return_value


def test_assign_government_add_edge(country):
    # Given
    govt = Mock()
    tax_payer = Mock()
    graph = country.graph
    graph.add_nodes_from([tax_payer, govt])

    # When
    country.assign_government(tax_payer, govt)

    # Then
    assert len(graph.edges) == 1
    assert graph.has_edge(govt, tax_payer)
    assert tax_payer.government is govt


def test_pay_taxes_to_government(country):
    # Given
    govt = Mock()
    tax_payer = Mock()

    # When
    country.pay_taxes(tax_payer, govt, 100)

    # Then
    govt.increase_flow.assert_any_call("taxes", 100)
    govt.increase_stock.assert_any_call("reserves", 100)
    tax_payer.increase_flow.assert_called_with("taxes", 100)
    tax_payer.decrease_stock.assert_called_with("cash", 100)
