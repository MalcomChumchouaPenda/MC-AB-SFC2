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


def test_requires_model_and_government_and_central_bank():
    # Assert
    expected = "missing 3 required positional arguments: "
    expected += "'model', 'government', and 'central_bank'"
    with pytest.raises(TypeError, match=expected):
        CountrySpace()


class FakeGovtRole(Mock):
    pass


class FakeCBRole(Mock):
    pass


@pytest.fixture
def init_args(monkeypatch):
    method = Mock(side_effect=lambda a, b, c: a())
    monkeypatch.setattr(CountrySpace, "add_role", method)
    monkeypatch.setattr("mc_ab_sfc.spaces.GovernmentRole", FakeGovtRole)
    monkeypatch.setattr("mc_ab_sfc.spaces.NationalCentralBankRole", FakeCBRole)
    model, govt, cb = Mock(), Mock(), Mock()
    return model, govt, cb


def test_init_and_create_government_role(init_args):
    # Given
    model, govt, cb = init_args

    # When
    country = CountrySpace(model, govt, cb)

    # Then
    country.add_role.assert_any_call(FakeGovtRole, govt, "government")
    assert isinstance(country.government_role, FakeGovtRole)


def test_init_and_create_central_bank_role(init_args):
    # Given
    model, govt, cb = init_args

    # When
    country = CountrySpace(model, govt, cb)

    # Then
    country.add_role.assert_any_call(FakeCBRole, cb, "central_bank")
    assert isinstance(country.central_bank_role, FakeCBRole)


def test_init_and_link_central_bank_and_govt(init_args):
    # Given
    model, govt, cb = init_args

    # When
    country = CountrySpace(model, govt, cb)

    # Then
    govt_role = country.government_role
    cb_role = country.central_bank_role
    assert country.graph.has_edge(govt_role, cb_role)
    assert cb_role.government is govt_role


@pytest.fixture
def country(init_args):
    # Given
    return CountrySpace(*init_args)


def test_contains_local_markets(country):
    # Assert
    assert hasattr(country, "markets")
    assert isinstance(country.markets, dict)


def test_exposes_inflation(country):
    # Given
    country.markets["goods"] = Mock(inflation=0.03)

    # Assert
    assert country.inflation == 0.03


def test_has_discount_rate(country):
    # Assert
    assert country.discount_rate == 0.0
    

# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


class FakePayerRole(Mock):
    pass


def test_add_tax_payer_creates_tax_payer_role(country, monkeypatch):
    # Given
    agent = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.TaxPayerRole", FakePayerRole)

    # When
    tax_payer = country.add_tax_payer(agent)

    # Then
    country.add_role.assert_any_call(FakePayerRole, agent, "tax_payer")
    assert isinstance(tax_payer, FakePayerRole)


def test_add_tax_payer_creates_edge_with_govt_role(country, monkeypatch):
    # Given
    monkeypatch.setattr("mc_ab_sfc.spaces.TaxPayerRole", FakePayerRole)
    govt_role = country.government_role
    graph = country.graph
    agent = Mock()

    # When
    tax_payer = country.add_tax_payer(agent)

    # Then
    assert graph.has_edge(govt_role, tax_payer)
    assert tax_payer.government is govt_role


class FakeBankRole(Mock):
    pass


def test_add_commercial_bank_creates_bank_role(country, monkeypatch):
    # Given
    agent = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.CommercialBankRole", FakeBankRole)

    # When
    bank_role = country.add_commercial_bank(agent)

    # Then
    country.add_role.assert_any_call(FakeBankRole, agent, "commercial_bank")
    assert isinstance(bank_role, FakeBankRole)


def test_add_commercial_bank_creates_edge_with_cb_role(country, monkeypatch):
    # Given
    monkeypatch.setattr("mc_ab_sfc.spaces.CommercialBankRole", FakeBankRole)
    cb_role = country.central_bank_role
    graph = country.graph
    agent = Mock()

    # When
    bank_role = country.add_commercial_bank(agent)

    # Then
    assert graph.has_edge(cb_role, bank_role)
    assert bank_role.central_bank is cb_role


class FakeBankAgent:
    pass


def test_pay_taxes_with_tax_payer_reserves(country, monkeypatch):
    # Given
    tax_payer = Mock(agent=FakeBankAgent())
    govt_role = country.government_role
    monkeypatch.setattr("mc_ab_sfc.spaces.BankAgent", FakeBankAgent)

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


class FakeHolderRole(Mock):
    pass


def test_add_equity_holder_creates_appropriate_role(country, monkeypatch):
    # Given
    household = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityHolderRole", FakeHolderRole)

    # When
    equity_holder = country.add_equity_holder(household)

    # Then
    country.add_role.assert_any_call(FakeHolderRole, household, "equity_holder")
    assert isinstance(equity_holder, FakeHolderRole)


class FakeIssuerRole(Mock):
    pass


def test_add_equity_issuer_creates_appropriate_role(country, monkeypatch):
    # Given
    agent = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityIssuerRole", FakeIssuerRole)

    # When
    equity_issuer = country.add_equity_issuer(agent)

    # Then
    country.add_role.assert_any_call(FakeIssuerRole, agent, "equity_issuer")
    assert isinstance(equity_issuer, FakeIssuerRole)


def test_assign_equity_holder_add_edge(country):
    # Given
    issuer = Mock()
    holder = Mock()
    graph = country.graph
    graph.add_nodes_from([issuer, holder])

    # When
    country.assign_equity_holder(issuer, holder, 0.5)

    # Then
    assert graph.has_edge(holder, issuer)
    assert graph[holder][issuer]["share"] == 0.5


def test_request_cash_advances(country):
    # Given
    bank_role = Mock()
    cb_role = country.central_bank_role
    country.graph.add_nodes_from([bank_role, cb_role])

    # When
    country.request_cash_advances(bank_role, 500)

    # Then
    bank_role.increase_stock.assert_any_call("reserves", 500)
    bank_role.increase_stock.assert_any_call("cash_advances", 500)
    cb_role.increase_stock.assert_any_call("reserves", 500)
    cb_role.increase_stock.assert_any_call("cash_advances", 500)


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


def test_distributes_dividends_with_reserves(country, issuer, holders, monkeypatch):
    # Given
    issuer.agent = FakeBankAgent()
    graph = country.graph
    graph.add_edge(issuer, holders[0], share=0.6)
    graph.add_edge(issuer, holders[1], share=0.4)
    monkeypatch.setattr("mc_ab_sfc.spaces.BankAgent", FakeBankAgent)

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


def test_update_statistics_with_goods_market_stats_updates(country):
    # Given
    goods_market = Mock()
    country.markets["goods"] = goods_market

    # When
    country.update_statistics()

    # Then
    goods_market.update_statistics.assert_called_once()
