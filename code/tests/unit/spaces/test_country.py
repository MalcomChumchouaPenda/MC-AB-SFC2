import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces.country import Country

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(Country, EcoSpace)


@pytest.fixture
def country():
    # Given
    model = Mock()
    country = Country(model)
    country.setup()
    return country


def test_has_default_agent_refs(country):
    # Assert
    assert country.government is None
    assert country.central_bank is None


def test_has_default_space_refs(country):
    # Assert
    assert country.union is None
    assert country.goods_market is None
    assert country.labor_market is None
    assert country.deposit_market is None


def test_exposes_inflation(country):
    # Given
    country.goods_market = Mock(inflation=0.03)

    # Assert
    assert country.inflation == 0.03


def test_exposes_average_price(country):
    # Given
    country.goods_market = Mock(average_price=10)

    # Assert
    assert country.average_price == 10


def test_exposes_average_productivity(country):
    # Given
    country.goods_market = Mock(average_productivity=1.5)

    # Assert
    assert country.average_productivity == 1.5


def test_exposes_average_wage(country):
    # Given
    country.labor_market = Mock(average_wage=15)

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
    country = Country(model)
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


class FakeFirm:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.tradable = False


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
    country.goods_market = goods_market

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
def country_before_firm_creation(monkeypatch):
    # Given
    model = Mock()
    country = Country(model)
    country.add_equity_issuer = Mock()
    country.assign_equity_holder = Mock()
    country.union = Mock()
    country.goods_market = Mock()
    country.labor_market = Mock()
    country.deposit_market = Mock()
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
    non_tradable_market = country.goods_market
    tradable_market = country.union.goods_market
    founders = [Mock(desired_equity=1000)]

    # When
    firm = country.create_firm(founders, tradable=False)

    # Then
    non_tradable_market.add_supplier.assert_called_with(firm)
    tradable_market.add_supplier.assert_not_called()


def test_create_firm_add_supplier_to_tradable_market(country_before_firm_creation):
    # Given
    country = country_before_firm_creation
    non_tradable_market = country.goods_market
    tradable_market = country.union.goods_market
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
    labor_market = country.labor_market
    founders = [Mock(desired_equity=1000)]

    # When
    firm = country.create_firm(founders, tradable=tradable)

    # Then
    labor_market.add_employer.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_borrower_role(country_before_firm_creation, tradable):
    # Given
    country = country_before_firm_creation
    credit_market = country.union.credit_market
    founders = [Mock(desired_equity=1000)]

    # When
    firm = country.create_firm(founders, tradable=tradable)

    # Then
    credit_market.add_borrower.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_client_role(country_before_firm_creation, tradable):
    # Given
    country = country_before_firm_creation
    deposit_market = country.deposit_market
    founders = [Mock(desired_equity=1000)]

    # When
    firm = country.create_firm(founders, tradable=tradable)

    # Then
    deposit_market.add_client.assert_called_with(firm)


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
    country = Country(model)
    country.add_equity_issuer = Mock()
    country.assign_equity_holder = Mock()
    country.union = Mock()
    country.goods_market = Mock()
    country.labor_market = Mock()
    country.deposit_market = Mock()
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
    founders = [Mock(desired_equity=1000)]
    country = country_before_bank_creation
    model = country.model

    # When
    bank = country.create_bank(founders)

    # Then
    model.banks.append.assert_called_with(bank)


def test_create_bank_add_bond_buyer(country_before_bank_creation):
    # Given
    founders = [Mock(desired_equity=1000)]
    country = country_before_bank_creation
    bond_market = country.union.bond_market

    # When
    bank = country.create_bank(founders)

    # Then
    bond_market.add_buyer.assert_called_with(bank)


def test_create_bank_add_lender_role(country_before_bank_creation):
    # Given
    founders = [Mock(desired_equity=1000)]
    country = country_before_bank_creation
    credit_market = country.union.credit_market

    # When
    bank = country.create_bank(founders)

    # Then
    credit_market.add_lender.assert_called_with(bank)


def test_create_bank_add_bank_role(country_before_bank_creation):
    # Given
    founders = [Mock(desired_equity=1000)]
    country = country_before_bank_creation
    deposit_market = country.deposit_market

    # When
    bank = country.create_bank(founders)

    # Then
    deposit_market.add_bank.assert_called_with(bank)


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
