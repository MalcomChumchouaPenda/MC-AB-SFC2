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
    return CountrySpace(model)


def test_has_government_role(country):
    # Assert
    assert country.government_role is None


def test_has_central_bank_role(country):
    # Assert
    assert country.central_bank_role is None


def test_contains_local_markets(country):
    # Assert
    assert hasattr(country, "markets")
    assert isinstance(country.markets, dict)


def test_exposes_inflation(country):
    # Given
    goods_market = Mock(inflation=0.03)
    country.markets = {"goods": goods_market}

    # Assert
    assert country.inflation == 0.03


def test_exposes_average_price(country):
    # Given
    goods_market = Mock(average_price=10)
    country.markets = {"goods": goods_market}

    # Assert
    assert country.average_price == 10


def test_exposes_average_productivity(country):
    # Given
    goods_market = Mock(average_productivity=1.5)
    country.markets = {"goods": goods_market}

    # Assert
    assert country.average_productivity == 1.5


def test_has_discount_rate(country):
    # Assert
    assert country.discount_rate == 0.0


# ---------------------------------------------------
# ROLES MANAGEMENT TESTS
# ----------------------------------------------------


@pytest.fixture
def country_with_roles():
    # Given
    model = Mock()
    country = CountrySpace(model)
    country.add_role = Mock(side_effect=lambda a, b, c: a())
    return country


class FakeGovtRole(Mock):
    pass


def test_add_government_role(country_with_roles, monkeypatch):
    # Given
    govt = Mock()
    country = country_with_roles
    monkeypatch.setattr("mc_ab_sfc.spaces.GovernmentRole", FakeGovtRole)

    # When
    govt_role = country.add_government(govt)

    # Then
    country.add_role.assert_any_call(FakeGovtRole, govt, "government")
    assert isinstance(govt_role, FakeGovtRole)
    assert govt_role == country.government_role


class FakeCBRole(Mock):
    pass


def test_add_central_bank_role(country_with_roles, monkeypatch):
    # Given
    govt_role = Mock()
    central_bank = Mock()
    country = country_with_roles
    country.government_role = govt_role
    monkeypatch.setattr("mc_ab_sfc.spaces.NationalCentralBankRole", FakeCBRole)

    # When
    cb_role = country.add_central_bank(central_bank)

    # Then
    country.add_role.assert_any_call(FakeCBRole, central_bank, "central_bank")
    assert isinstance(cb_role, FakeCBRole)
    assert cb_role is country.central_bank_role


def test_add_central_bank_role_creates_links(country_with_roles, monkeypatch):
    # Given
    govt_role = Mock()
    central_bank = Mock()
    country = country_with_roles
    country.government_role = govt_role
    monkeypatch.setattr("mc_ab_sfc.spaces.NationalCentralBankRole", FakeCBRole)

    # When
    cb_role = country.add_central_bank(central_bank)

    # Then
    assert country.graph.has_edge(govt_role, cb_role)
    assert cb_role.government is govt_role


class FakePayerRole(Mock):
    pass


def test_add_tax_payer_role(country_with_roles, monkeypatch):
    # Given
    agent = Mock()
    govt_role = Mock()
    country = country_with_roles
    country.government_role = govt_role
    monkeypatch.setattr("mc_ab_sfc.spaces.TaxPayerRole", FakePayerRole)

    # When
    payer_role = country.add_tax_payer(agent)

    # Then
    country.add_role.assert_any_call(FakePayerRole, agent, "tax_payer")
    assert isinstance(payer_role, FakePayerRole)


def test_add_tax_payer_role_creates_links(country_with_roles, monkeypatch):
    # Given
    agent = Mock()
    govt_role = Mock()
    country = country_with_roles
    country.government_role = govt_role
    monkeypatch.setattr("mc_ab_sfc.spaces.TaxPayerRole", FakePayerRole)

    # When
    payer_role = country.add_tax_payer(agent)

    # Then
    assert country.graph.has_edge(govt_role, payer_role)
    assert payer_role.government is govt_role


class FakeBankRole(Mock):
    pass


def test_add_commercial_bank_role(country_with_roles, monkeypatch):
    # Given
    agent = Mock()
    cb_role = Mock()
    country = country_with_roles
    country.central_bank_role = cb_role
    monkeypatch.setattr("mc_ab_sfc.spaces.CommercialBankRole", FakeBankRole)

    # When
    bank_role = country.add_commercial_bank(agent)

    # Then
    country.add_role.assert_any_call(FakeBankRole, agent, "commercial_bank")
    assert isinstance(bank_role, FakeBankRole)


def test_add_commercial_bank_role_creates_links(country_with_roles, monkeypatch):
    # Given
    agent = Mock()
    cb_role = Mock()
    country = country_with_roles
    country.central_bank_role = cb_role
    monkeypatch.setattr("mc_ab_sfc.spaces.CommercialBankRole", FakeBankRole)

    # When
    bank_role = country.add_commercial_bank(agent)

    # Then
    assert country.graph.has_edge(cb_role, bank_role)
    assert bank_role.central_bank is cb_role


class FakeHolderRole(Mock):
    pass


def test_add_equity_holder_role(country_with_roles, monkeypatch):
    # Given
    household = Mock()
    country = country_with_roles
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityHolderRole", FakeHolderRole)

    # When
    holder_role = country.add_equity_holder(household)

    # Then
    country.add_role.assert_any_call(FakeHolderRole, household, "equity_holder")
    assert isinstance(holder_role, FakeHolderRole)


class FakeIssuerRole(Mock):
    pass


def test_add_equity_issuer_creates_appropriate_role(country_with_roles, monkeypatch):
    # Given
    agent = Mock()
    country = country_with_roles
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityIssuerRole", FakeIssuerRole)

    # When
    issuer_role = country.add_equity_issuer(agent)

    # Then
    country.add_role.assert_any_call(FakeIssuerRole, agent, "equity_issuer")
    assert isinstance(issuer_role, FakeIssuerRole)


def test_assign_equity_holder_to_equity_issuer(country):
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


# ---------------------------------------------------
# TRANSACTIONS MANAGEMENT
# ----------------------------------------------------


class FakeBankAgent(Mock):
    pass


def test_pay_taxes_with_tax_payer_reserves(country, monkeypatch):
    # Given
    govt_role = Mock()
    country.government_role = govt_role
    payer_role = Mock(agent=FakeBankAgent())
    monkeypatch.setattr("mc_ab_sfc.spaces.BankAgent", FakeBankAgent)

    # When
    country.pay_taxes(payer_role, 100)

    # Then
    govt_role.increase_flow.assert_any_call("taxes", 100)
    govt_role.increase_stock.assert_any_call("reserves", 100)
    payer_role.increase_flow.assert_called_with("taxes", 100)
    payer_role.decrease_stock.assert_called_with("reserves", 100)


def test_pay_taxes_with_tax_payer_cash(country):
    # Given
    payer_role = Mock()
    govt_role = Mock()
    country.government_role = govt_role

    # When
    country.pay_taxes(payer_role, 100)

    # Then
    govt_role.increase_flow.assert_any_call("taxes", 100)
    govt_role.increase_stock.assert_any_call("reserves", 100)
    payer_role.increase_flow.assert_called_with("taxes", 100)
    payer_role.decrease_stock.assert_called_with("cash", 100)


def test_request_cash_advances(country):
    # Given
    bank_role = Mock()
    cb_role = Mock()
    country.central_bank_role = cb_role
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


class FakeHouseholdAgent(Mock):
    pass


def test_get_households_returns_household_agent_roles(country, monkeypatch):
    # Given
    monkeypatch.setattr("mc_ab_sfc.spaces.TaxPayerRole", FakePayerRole)
    monkeypatch.setattr("mc_ab_sfc.spaces.HouseholdAgent", FakeHouseholdAgent)
    household_roles = [FakePayerRole(agent=FakeHouseholdAgent()) for _ in range(6)]
    payer_roles = [FakePayerRole() for _ in range(5)]
    other_roles = [Mock() for _ in range(5)]
    country.graph.add_nodes_from(household_roles + payer_roles + other_roles)

    # When
    result = country.get_households()

    # Then
    assert result == household_roles


def test_transfer_profit_to_government(country):
    # Given
    cb_role, govt_role = Mock(), Mock()
    cb_role.government = govt_role

    # When
    country.transfer_profit(cb_role, 100)

    # Then
    cb_role.increase_stock.assert_called_once_with("reserves", 100)
    cb_role.increase_flow.assert_called_once_with("profit", 100)
    govt_role.increase_stock.assert_called_once_with("reserves", 100)
    govt_role.increase_flow.assert_called_once_with("profit", 100)


def test_pay_public_transfers_to_household(country):
    # Given
    govt_role = Mock()
    household_role = Mock()

    # When
    country.pay_public_transfers(govt_role, household_role, 100)

    # Then
    household_role.increase_stock.assert_called_once_with("cash", 100)
    household_role.increase_flow.assert_called_once_with("public_transfers", 100)
    govt_role.decrease_stock.assert_called_once_with("reserves", 100)
    govt_role.increase_flow.assert_called_once_with("public_transfers", 100)


def test_update_statistics_with_goods_market_stats_updates(country):
    # Given
    goods_market = Mock()
    country.markets["goods"] = goods_market

    # When
    country.update_statistics()

    # Then
    goods_market.update_statistics.assert_called_once()


class FakeHolderRole(Mock):
    pass

def test_get_only_eligible_investors(country, monkeypatch):
    # Given
    other = Mock()
    eligible = FakeHolderRole(desired_equity=100, equity=0)
    ineligible = FakeHolderRole(desired_equity=100, equity=10)
    country.graph.add_nodes_from([eligible, ineligible, other])
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityHolderRole", FakeHolderRole)

    # When
    investors =  country.get_potential_investors()

    # Then
    assert investors == [eligible]


def test_get_investors_excludes_initiating_household(country, monkeypatch):
    # Given
    initiator = FakeHolderRole(desired_equity=100, equity=0)
    eligible = FakeHolderRole(desired_equity=100, equity=0)
    country.graph.add_nodes_from([initiator, eligible])
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityHolderRole", FakeHolderRole)

    # When
    investors =  country.get_potential_investors(exclude=initiator)

    # Then
    assert investors == [eligible]