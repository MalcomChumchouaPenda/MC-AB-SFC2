import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces.country import CountrySpace

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


def test_has_firm_roles(country):
    # Assert
    assert country.firm_roles == []


def test_has_bank_roles(country):
    # Assert
    assert country.bank_roles == []


def test_contains_local_markets(country):
    # Assert
    assert hasattr(country, "markets")
    assert isinstance(country.markets, dict)


def test_contains_monetary_union_ref(country):
    # Assert
    assert country.monetary_union is None


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


def test_exposes_average_wage(country):
    # Given
    labor_market = Mock(average_wage=15)
    country.markets = {"labor": labor_market}

    # Assert
    assert country.average_wage == 15


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


class FakeHolderRole(Mock):
    pass


def test_add_equity_holder_role(country_with_roles, monkeypatch):
    # Given
    household = Mock()
    country = country_with_roles
    monkeypatch.setattr("mc_ab_sfc.spaces.country.EquityHolderRole", FakeHolderRole)

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
    monkeypatch.setattr("mc_ab_sfc.spaces.country.EquityIssuerRole", FakeIssuerRole)

    # When
    issuer_role = country.add_equity_issuer(agent)

    # Then
    country.add_role.assert_any_call(FakeIssuerRole, agent, "equity_issuer")
    assert isinstance(issuer_role, FakeIssuerRole)


class FakeBank:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def test_add_equity_issuer_registers_bank_role(country_with_roles, monkeypatch):
    # Given
    agent = FakeBank()
    country = country_with_roles
    monkeypatch.setattr("mc_ab_sfc.spaces.country.EquityIssuerRole", FakeIssuerRole)
    monkeypatch.setattr("mc_ab_sfc.spaces.country.Bank", FakeBank)

    # When
    issuer_role = country.add_equity_issuer(agent)

    # Then
    assert country.bank_roles == [issuer_role]


class FakeFirm:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.tradable = False


def test_add_equity_issuer_registers_firm_role(country_with_roles, monkeypatch):
    # Given
    agent = FakeFirm()
    country = country_with_roles
    monkeypatch.setattr("mc_ab_sfc.spaces.country.EquityIssuerRole", FakeIssuerRole)
    monkeypatch.setattr("mc_ab_sfc.spaces.country.Firm", FakeFirm)

    # When
    issuer_role = country.add_equity_issuer(agent)

    # Then
    assert country.firm_roles == [issuer_role]


def test_assign_equity_holder_to_equity_issuer(country):
    # Given
    issuer = Mock()
    holder = Mock()
    graph = country.graph
    graph.add_nodes_from([issuer, holder])

    # When
    country.assign_equity_holder(issuer, holder)

    # Then
    assert graph.has_edge(holder, issuer)
    assert holder.equity_issuer is issuer


# ---------------------------------------------------
# TRANSACTIONS MANAGEMENT
# ----------------------------------------------------


@pytest.fixture
def issuer(country):
    # Given
    issuer = Mock()
    country.graph.add_node(issuer)
    return issuer


@pytest.fixture
def holders(country):
    # Given
    holders = [Mock(share=0.6), Mock(share=0.4), Mock()]
    country.graph.add_nodes_from(holders)
    return holders


def test_updates_shares(country, issuer, holders):
    # Given
    issuer.equity = 100
    holders[0].equity = 70
    holders[1].equity = 30
    graph = country.graph
    graph.add_edge(issuer, holders[0])
    graph.add_edge(issuer, holders[1])

    # When
    country.update_equity_shares(issuer)

    # Then
    assert holders[0].share == 0.7
    assert holders[1].share == 0.3


def test_distributes_dividends_with_reserves(country, issuer, holders, monkeypatch):
    # Given
    issuer.agent = FakeBank()
    graph = country.graph
    graph.add_edge(issuer, holders[0])
    graph.add_edge(issuer, holders[1])
    monkeypatch.setattr("mc_ab_sfc.spaces.country.Bank", FakeBank)

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
    graph.add_edge(issuer, holders[0])
    graph.add_edge(issuer, holders[1])

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
    graph.add_edge(issuer, holders[0])
    graph.add_edge(issuer, holders[1])
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


class FakeHousehold:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


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
    monkeypatch.setattr("mc_ab_sfc.spaces.country.EquityHolderRole", FakeHolderRole)

    # When
    investors = country.get_potential_investors()

    # Then
    assert investors == [eligible]


def test_get_investors_excludes_initiating_household(country, monkeypatch):
    # Given
    initiator = FakeHolderRole(desired_equity=100, equity=0)
    eligible = FakeHolderRole(desired_equity=100, equity=0)
    country.graph.add_nodes_from([initiator, eligible])
    monkeypatch.setattr("mc_ab_sfc.spaces.country.EquityHolderRole", FakeHolderRole)

    # When
    investors = country.get_potential_investors(exclude=initiator)

    # Then
    assert investors == [eligible]


@pytest.fixture
def monetary_union():
    # Given
    union = Mock()
    union.markets = {"goods": Mock()}
    return union


@pytest.fixture
def country_before_firm_creation(monkeypatch, monetary_union):
    # Given
    model = Mock()
    country = CountrySpace(model)
    country.add_equity_issuer = Mock()
    country.assign_equity_holder = Mock()
    country.monetary_union = monetary_union
    country.markets = {
        "labor": Mock(),
        "goods": Mock(),
        "deposit": Mock(),
        "credit": Mock(),
    }
    monkeypatch.setattr("mc_ab_sfc.spaces.country.Firm", FakeFirm)
    return country


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_creates_firm_agent(country_before_firm_creation, tradable):
    # Given
    country = country_before_firm_creation
    founders = [Mock(desired_equity=500) for _ in range(2)]

    # When
    firm = country.create_firm(founders, tradable=tradable)

    # Then
    assert firm.args == (country.model,)
    assert isinstance(firm, FakeFirm)
    assert firm.tradable == tradable


def test_create_firm_registers_firm_in_model(country_before_firm_creation):
    # Given
    country = country_before_firm_creation
    model = country.model
    founders = [Mock(desired_equity=1000)]

    # When
    firm = country.create_firm(founders, tradable=True)

    # Then
    model.firms.append.assert_called_with(firm)


def test_create_firm_add_supplier_to_non_tradable_market(country_before_firm_creation):
    # Given
    country = country_before_firm_creation
    non_tradable_market = country.markets["goods"]
    tradable_market = country.monetary_union.markets["goods"]
    founders = [Mock(desired_equity=1000)]

    # When
    firm = country.create_firm(founders, tradable=False)

    # Then
    non_tradable_market.add_supplier.assert_called_with(firm)
    tradable_market.add_supplier.assert_not_called()


def test_create_firm_add_supplier_to_tradable_market(country_before_firm_creation):
    # Given
    country = country_before_firm_creation
    non_tradable_market = country.markets["goods"]
    tradable_market = country.monetary_union.markets["goods"]
    founders = [Mock(desired_equity=1000)]

    # When
    firm = country.create_firm(founders, tradable=True)

    # Then
    tradable_market.add_supplier.assert_called_with(firm)
    non_tradable_market.add_supplier.assert_not_called()


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_employer_role(country_before_firm_creation, tradable):
    # Given
    country = country_before_firm_creation
    market = country.markets["labor"]
    founders = [Mock(desired_equity=1000)]

    # When
    firm = country.create_firm(founders, tradable=tradable)

    # Then
    market.add_employer.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_borrower_role(country_before_firm_creation, tradable):
    # Given
    country = country_before_firm_creation
    market = country.markets["credit"]
    founders = [Mock(desired_equity=1000)]

    # When
    firm = country.create_firm(founders, tradable=tradable)

    # Then
    market.add_borrower.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_client_role(country_before_firm_creation, tradable):
    # Given
    country = country_before_firm_creation
    market = country.markets["deposit"]
    founders = [Mock(desired_equity=1000)]

    # When
    firm = country.create_firm(founders, tradable=tradable)

    # Then
    market.add_client.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_equity_issuer_role(country_before_firm_creation, tradable):
    # Given
    country = country_before_firm_creation
    founders = [Mock(desired_equity=1000)]

    # When
    firm = country.create_firm(founders, tradable=tradable)

    # Then
    country.add_equity_issuer.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_builds_equity_links(country_before_firm_creation, tradable):
    # Given
    issuer = Mock()
    country = country_before_firm_creation
    country.add_equity_issuer.return_value = issuer
    founders = [Mock(desired_equity=500) for _ in range(2)]

    # When
    country.create_firm(founders, tradable=tradable)

    # Then
    for founder in founders:
        country.assign_equity_holder.assert_any_call(issuer, founder)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_builds_initial_equity(country_before_firm_creation, tradable):
    # Given
    issuer = Mock()
    country = country_before_firm_creation
    country.add_equity_issuer.return_value = issuer
    founders = [Mock(desired_equity=500) for _ in range(2)]

    # When
    country.create_firm(founders, tradable=tradable)

    # Then
    issuer.increase_stock.assert_any_call("equity", 1000)
    issuer.increase_stock.assert_any_call("cash", 1000)
    for founder in founders:
        founder.increase_stock.assert_any_call("equity", 500)
        founder.decrease_stock.assert_any_call("cash", 500)


@pytest.fixture
def country_before_bank_creation(monkeypatch):
    # Given
    model = Mock()
    country = CountrySpace(model)
    country.add_equity_issuer = Mock()
    country.assign_equity_holder = Mock()
    country.markets = {
        "deposit": Mock(),
        "credit": Mock(),
    }
    monkeypatch.setattr("mc_ab_sfc.spaces.country.Bank", FakeBank)
    return country


def test_create_bank_creates_bank_agent(country_before_bank_creation):
    # Given
    country = country_before_bank_creation
    founders = [Mock(desired_equity=500) for _ in range(2)]

    # When
    bank = country.create_bank(founders)

    # Then
    assert bank.args == (country.model,)
    assert isinstance(bank, FakeBank)


def test_create_bank_registers_bank_in_model(country_before_bank_creation):
    # Given
    country = country_before_bank_creation
    model = country.model
    founders = [Mock(desired_equity=1000)]

    # When
    bank = country.create_bank(founders)

    # Then
    model.banks.append.assert_called_with(bank)


def test_create_bank_add_bond_buyer(country_before_bank_creation):
    # Given
    country = country_before_bank_creation
    market = country.model.bond_market
    founders = [Mock(desired_equity=1000)]

    # When
    bank = country.create_bank(founders)

    # Then
    market.add_buyer.assert_called_with(bank)


def test_create_bank_add_lender_role(country_before_bank_creation):
    # Given
    country = country_before_bank_creation
    market = country.markets["credit"]
    founders = [Mock(desired_equity=1000)]

    # When
    bank = country.create_bank(founders)

    # Then
    market.add_lender.assert_called_with(bank)


def test_create_bank_add_bank_role(country_before_bank_creation):
    # Given
    country = country_before_bank_creation
    market = country.markets["deposit"]
    founders = [Mock(desired_equity=1000)]

    # When
    bank = country.create_bank(founders)

    # Then
    market.add_bank.assert_called_with(bank)


def test_create_bank_add_equity_issuer_role(country_before_bank_creation):
    # Given
    country = country_before_bank_creation
    founders = [Mock(desired_equity=1000)]

    # When
    bank = country.create_bank(founders)

    # Then
    country.add_equity_issuer.assert_called_with(bank)


def test_create_bank_builds_equity_links(country_before_bank_creation):
    # Given
    issuer = Mock()
    country = country_before_bank_creation
    country.add_equity_issuer.return_value = issuer
    founders = [Mock(desired_equity=500) for _ in range(2)]

    # When
    country.create_bank(founders)

    # Then
    for founder in founders:
        country.assign_equity_holder.assert_any_call(issuer, founder)


def test_create_bank_builds_initial_equity(country_before_bank_creation):
    # Given
    issuer = Mock()
    country = country_before_bank_creation
    country.add_equity_issuer.return_value = issuer
    founders = [Mock(desired_equity=500) for _ in range(2)]

    # When
    country.create_bank(founders)

    # Then
    issuer.increase_stock.assert_any_call("equity", 1000)
    issuer.increase_stock.assert_any_call("reserves", 1000)
    for founder in founders:
        founder.increase_stock.assert_any_call("equity", 500)
        founder.decrease_stock.assert_any_call("cash", 500)
