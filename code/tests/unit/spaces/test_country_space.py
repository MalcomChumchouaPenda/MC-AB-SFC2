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


def test_requires_model_and_government():
    # Assert
    expected = "required positional arguments: 'model' and 'government'"
    with pytest.raises(TypeError, match=expected):
        CountrySpace()


class FakeRole:
    pass


def test_creates_and_registers_government_role(monkeypatch):
    # Given
    model, govt, govt_role = Mock(), Mock(), Mock()
    monkeypatch.setattr(CountrySpace, "add_role", Mock(return_value=govt_role))
    monkeypatch.setattr("mc_ab_sfc.spaces.GovernmentRole", FakeRole)

    # When
    country = CountrySpace(model, govt)

    # Then
    country.add_role.assert_called_with(FakeRole, govt, "government_role")
    assert country.government_role is govt_role


@pytest.fixture
def country(monkeypatch):
    # Given
    model, govt, govt_role = Mock(), Mock(), Mock()
    monkeypatch.setattr(CountrySpace, "add_role", Mock(return_value=govt_role))
    monkeypatch.setattr("mc_ab_sfc.spaces.GovernmentRole", FakeRole)
    country = CountrySpace(model, govt)
    return country


def test_contains_local_markets(country):
    # Assert
    assert hasattr(country, "markets")
    assert isinstance(country.markets, dict)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


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


def test_add_tax_payer_creates_edge_with_govt_role(country, monkeypatch):
    # Given
    tax_payer, agent = Mock(), Mock()
    country.add_role = Mock(return_value=tax_payer)
    monkeypatch.setattr("mc_ab_sfc.spaces.TaxPayerRole", FakeRole)
    govt_role = country.government_role
    graph = country.graph

    # When
    country.add_tax_payer(agent)

    # Then
    assert len(graph.edges) == 1
    assert graph.has_edge(govt_role, tax_payer)
    assert tax_payer.government is govt_role


class FakeAgent:
    pass


def test_pay_taxes_with_tax_payer_reserves(country, monkeypatch):
    # Given
    tax_payer = Mock(agent=FakeAgent())
    govt_role = country.government_role
    monkeypatch.setattr("mc_ab_sfc.spaces.BankAgent", FakeAgent)

    # When
    country.pay_taxes(tax_payer, 100)

    # Then
    govt_role.increase_flow.assert_any_call("taxes", 100)
    govt_role.increase_stock.assert_any_call("reserves", 100)
    tax_payer.increase_flow.assert_called_with("taxes", 100)
    tax_payer.decrease_stock.assert_called_with("reserves", 100)


def test_pay_taxes_with_tax_payer_cash(country):
    # Given
    tax_payer = Mock()
    govt_role = country.government_role

    # When
    country.pay_taxes(tax_payer, 100)

    # Then
    govt_role.increase_flow.assert_any_call("taxes", 100)
    govt_role.increase_stock.assert_any_call("reserves", 100)
    tax_payer.increase_flow.assert_called_with("taxes", 100)
    tax_payer.decrease_stock.assert_called_with("cash", 100)


def test_add_equity_holder_creates_appropriate_role(country, monkeypatch):
    # Given
    household = Mock()
    country.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityHolderRole", FakeRole)

    # When
    equity_holder = country.add_equity_holder(household)

    # Then
    country.add_role.assert_called_with(FakeRole, household, "equity_holder")
    assert equity_holder is country.add_role.return_value


def test_add_equity_issuer_creates_appropriate_role(country, monkeypatch):
    # Given
    agent = Mock()
    country.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityIssuerRole", FakeRole)

    # When
    equity_issuer = country.add_equity_issuer(agent)

    # Then
    country.add_role.assert_called_with(FakeRole, agent, "equity_issuer")
    assert equity_issuer is country.add_role.return_value


def test_assign_equity_holder_add_edge(country):
    # Given
    issuer = Mock()
    holder = Mock()
    graph = country.graph
    graph.add_nodes_from([issuer, holder])

    # When
    country.assign_equity_holder(issuer, holder, 0.5)

    # Then
    assert len(graph.edges) == 1
    assert graph.has_edge(holder, issuer)
    assert graph[holder][issuer]["share"] == 0.5


@pytest.fixture
def issuer(country):
    # Given
    issuer = Mock()
    country.graph.add_node(issuer)
    return issuer


@pytest.fixture
def holders(country):
    # Given
    holders = [Mock() for _ in range(3)]
    country.graph.add_nodes_from(holders)
    return holders


class FakeAgent:
    pass


def test_distributes_dividends_with_reserves(country, issuer, holders, monkeypatch):
    # Given
    issuer.agent = FakeAgent()
    graph = country.graph
    graph.add_edge(issuer, holders[0], share=0.6)
    graph.add_edge(issuer, holders[1], share=0.4)
    monkeypatch.setattr("mc_ab_sfc.spaces.BankAgent", FakeAgent)

    # When
    country.distribute_dividends(issuer, 200)

    # Then
    issuer.increase_flow.assert_called_with("dividends", 200)
    issuer.decrease_stock.assert_called_with("reserves", 200)
    holders[0].increase_flow.assert_called_with("dividends", 120)
    holders[0].increase_stock.assert_called_with("cash", 120)
    holders[1].increase_flow.assert_called_with("dividends", 80)
    holders[1].increase_stock.assert_called_with("cash", 80)


def test_distributes_dividends_with_cash(country, issuer, holders):
    # Given
    graph = country.graph
    graph.add_edge(issuer, holders[0], share=0.6)
    graph.add_edge(issuer, holders[1], share=0.4)

    # When
    country.distribute_dividends(issuer, 200)

    # Then
    issuer.increase_flow.assert_called_with("dividends", 200)
    issuer.decrease_stock.assert_called_with("cash", 200)
    holders[0].increase_flow.assert_called_with("dividends", 120)
    holders[0].increase_stock.assert_called_with("cash", 120)
    holders[1].increase_flow.assert_called_with("dividends", 80)
    holders[1].increase_stock.assert_called_with("cash", 80)


def test_update_equity_holdings(country, issuer, holders):
    # Given
    graph = country.graph
    graph.add_edge(issuer, holders[0], share=0.6)
    graph.add_edge(issuer, holders[1], share=0.4)
    issuer.net_worth = 1200

    # When
    country.update_equity_holdings(issuer)

    # Then
    issuer.clear_stock.assert_called_once_with("equity")
    issuer.increase_stock.assert_called_once_with("equity", 1200)
    holders[0].clear_stock.assert_called_once_with("equity")
    holders[0].increase_stock.assert_called_once_with("equity", 720)
    holders[1].clear_stock.assert_called_once_with("equity")
    holders[1].increase_stock.assert_called_once_with("equity", 480)
