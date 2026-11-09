import pytest
from collections import defaultdict
from unittest.mock import Mock, call
from model.spaces.country import Country

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.extensions import EcoSpace

    # When
    is_derived = issubclass(Country, EcoSpace)

    # Then
    assert is_derived


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    return model


def test_initializes_pos(model):
    # When
    country = Country(model)

    # Then
    assert country.pos == 0


def test_initializes_inflation(model):
    # When
    country = Country(model)

    # Then
    assert country.inflation == 0


def test_initializes_gdp(model):
    # When
    country = Country(model)

    # Then
    assert country.gdp == 0


def test_initializes_prob_failure(model):
    # When
    country = Country(model)

    # Then
    assert country.prob_failure == 0


def test_initializes_tax_rate(model):
    # Given
    model.p.initial_tax_rate = 0.21

    # When
    country = Country(model)

    # Then
    assert country.tax_rate == 0.21


def test_initializes_discount_rate(model):
    # Given
    model.p.initial_discount_rate = 0.01

    # When
    country = Country(model)

    # Then
    assert country.discount_rate == 0.01


def test_initializes_fiscal_authority(model):
    # When
    country = Country(model)

    # Then
    assert country.fiscal_authority is None


def test_initializes_monetary_authority(model):
    # When
    country = Country(model)

    # Then
    assert country.monetary_authority is None


def test_exposes_average_wage_from_labor_market(model):
    # Given
    country = Country(model)
    country.spaces["labor_market"] = Mock(average_wage=15)

    # When
    exposed = country.average_wage

    # Then
    assert exposed == 15


# ---------------------------------------------------
# SUB SPACES CREATION
# ----------------------------------------------------


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.pos = 2
    return country


FakeGoodMarket = Mock()
FakeLaborMarket = Mock()
FakeDepositMarket = Mock()


@pytest.fixture
def country_without_markets(monkeypatch, country):
    # Given
    monkeypatch.setattr("model.spaces.country.GoodsMarket", FakeGoodMarket)
    monkeypatch.setattr("model.spaces.country.LaborMarket", FakeLaborMarket)
    monkeypatch.setattr("model.spaces.country.DepositMarket", FakeDepositMarket)
    country.add_space = Mock()
    return country


def test_create_markets_adds_goods_market(country_without_markets):
    # Given
    country = country_without_markets

    # When
    country.create_markets()

    # Then
    country.add_space.assert_any_call(FakeGoodMarket, "goods_market", tradable=False)


def test_create_markets_adds_labor_market(country_without_markets):
    # Given
    country = country_without_markets

    # When
    country.create_markets()

    # Then
    country.add_space.assert_any_call(FakeLaborMarket, "labor_market")


def test_create_markets_adds_deposit_market(country_without_markets):
    # Given
    country = country_without_markets

    # When
    country.create_markets()

    # Then
    country.add_space.assert_any_call(FakeDepositMarket, "deposit_market")


def test_create_markets_sets_deposit_market_country_pos(country_without_markets):
    # Given
    market = Mock()
    country = country_without_markets
    country.add_space = lambda a, *b, **c: market if a is FakeDepositMarket else Mock()

    # When
    country.create_markets()

    # Then
    assert market.country_pos == country.pos


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


@pytest.fixture
def before_adding_agent(country):
    # Given
    country.add_role = Mock()
    return country


@pytest.fixture
def before_adding_central_bank(monkeypatch, before_adding_agent):
    # Given
    FakeRole = Mock()
    monkeypatch.setattr("model.spaces.country.MonetaryAuthority", FakeRole)
    country = before_adding_agent
    return country, FakeRole


def test_add_central_bank_add_monetary_authority_role(before_adding_central_bank):
    # Given
    cb = Mock(country_pos=2)
    country, FakeRole = before_adding_central_bank

    # When
    country.add_central_bank(cb)

    # Then
    country.add_role.assert_called_with(FakeRole, cb)


def test_add_central_bank_sets_monetary_authority(before_adding_central_bank):
    # Given
    role = Mock()
    cb = Mock(country_pos=2)
    country, _ = before_adding_central_bank
    country.add_role.return_value = role

    # When
    country.add_central_bank(cb)

    # Then
    assert country.monetary_authority is role


def test_add_central_bank_does_nothing_for_foreign(before_adding_central_bank):
    # Given
    role = Mock()
    cb = Mock(country_pos=3)
    country, _ = before_adding_central_bank
    country.add_role.return_value = role

    # When
    country.add_central_bank(cb)

    # Then
    country.add_role.assert_not_called()
    assert country.monetary_authority is None


@pytest.fixture
def before_adding_government(monkeypatch, before_adding_agent):
    # Given
    FakeRole = Mock()
    monkeypatch.setattr("model.spaces.country.FiscalAuthority", FakeRole)
    country = before_adding_agent
    country.monetary_authority = Mock(id=1)
    return country, FakeRole


def test_add_government_add_fiscal_authority_role(before_adding_government):
    # Given
    govt = Mock(country_pos=2)
    country, FakeRole = before_adding_government

    # When
    country.add_government(govt)

    # Then
    country.add_role.assert_called_with(FakeRole, govt)


def test_add_government_sets_fiscal_authority(before_adding_government):
    # Given
    role = Mock()
    govt = Mock(country_pos=2)
    country, *_ = before_adding_government
    country.add_role.return_value = role

    # When
    country.add_government(govt)

    # Then
    assert country.fiscal_authority == role


def test_add_government_does_nothing_if_foreigner(before_adding_government):
    # Given
    govt = Mock(country_pos=3)
    country, *_ = before_adding_government

    # When
    country.add_government(govt)

    # Then
    assert not country.add_role.called
    assert country.fiscal_authority is None


@pytest.fixture
def before_adding_household(monkeypatch, before_adding_agent):
    # Given
    FakeRole = Mock()
    monkeypatch.setattr("model.spaces.country.Citizen", FakeRole)
    country = before_adding_agent
    country.monetary_authority = Mock(id=1)
    return country, FakeRole


def test_add_household_add_citizen_role(before_adding_household):
    # Given
    household = Mock(country_pos=2)
    country, FakeRole = before_adding_household

    # When
    country.add_household(household)

    # Then
    country.add_role.assert_called_with(FakeRole, household)


def test_add_household_does_nothing_if_foreigner(before_adding_household):
    # Given
    household = Mock(country_pos=3)
    country, *_ = before_adding_household

    # When
    country.add_household(household)

    # Then
    assert not country.add_role.called


@pytest.fixture
def before_adding_firm(monkeypatch, before_adding_agent):
    # Given
    FakeRole = Mock()
    monkeypatch.setattr("model.spaces.country.Company", FakeRole)
    country = before_adding_agent
    country.monetary_authority = Mock(id=1)
    return country, FakeRole


@pytest.mark.parametrize("tradable", [True, False])
def test_add_firm_add_company_role(before_adding_firm, tradable):
    # Given
    firm = Mock(tradable=tradable, country_pos=2)
    country, FakeRole = before_adding_firm

    # When
    country.add_firm(firm)

    # Then
    country.add_role.assert_called_with(FakeRole, firm)


@pytest.mark.parametrize("tradable, sector", [(True, "FT"), (False, "FNT")])
def test_add_firm_sets_company_sector(before_adding_firm, tradable, sector):
    # Given
    role = Mock()
    firm = Mock(tradable=tradable, country_pos=2)
    country, *_ = before_adding_firm
    country.add_role.return_value = role

    # When
    country.add_firm(firm)

    # Then
    assert role.sector == sector


@pytest.mark.parametrize("tradable", [(True, False)])
def test_add_firm_does_nothing_if_foreigner(before_adding_firm, tradable):
    # Given
    firm = Mock(tradable=tradable, country_pos=3)
    country, *_ = before_adding_firm

    # When
    country.add_firm(firm)

    # Then
    assert not country.add_role.called


@pytest.fixture
def before_adding_bank(monkeypatch, before_adding_agent):
    # Given
    FakeRole = Mock()
    monkeypatch.setattr("model.spaces.country.Company", FakeRole)
    country = before_adding_agent
    country.monetary_authority = Mock(id=1)
    return country, FakeRole


def test_add_bank_add_company_role(before_adding_bank):
    # Given
    bank = Mock(id=2, country_pos=2)
    country, FakeRole = before_adding_bank

    # When
    country.add_bank(bank)

    # Then
    country.add_role.assert_called_with(FakeRole, bank)


def test_add_bank_sets_company_sector(before_adding_bank):
    # Given
    role = Mock()
    bank = Mock(country_pos=2)
    country, *_ = before_adding_bank
    country.add_role.return_value = role

    # When
    country.add_bank(bank)

    # Then
    assert role.sector == "B"


def test_add_bank_does_nothing_if_foreigner(before_adding_bank):
    # Given
    bank = Mock(country_pos=3)
    country, *_ = before_adding_bank

    # When
    country.add_bank(bank)

    # Then
    assert not country.add_role.called


# ---------------------------------------------------
# CURRENT INDICATORS
# ----------------------------------------------------


@pytest.fixture
def country_with_roles(country):
    # Given
    roles = {}
    country.roles = roles
    return country, roles


@pytest.fixture
def country_with_two_groups(country_with_roles, make_dlist):
    # Given
    country, roles = country_with_roles
    companies = make_dlist([Mock(id=i) for i in range(12)])
    companies.name = "company"
    roles.update({role.id: role for role in companies})
    group1 = make_dlist(companies[:10])
    group2 = make_dlist(companies[10:])
    return country, group1, group2


def test_calc_bank_number_ratio(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector = "F"
    group2.sector = "B"

    # When
    ratio = country.calc_bank_number_ratio()

    # Then
    assert ratio == 0.2


def test_calc_bank_number_ratio_if_no_firms(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector = "B"
    group2.sector = "B"

    # When
    ratio = country.calc_bank_number_ratio()

    # Then
    assert ratio == 1.0


def test_calc_bank_equity_ratio(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group1.equity = "F", 50
    group2.sector, group2.equity = "B", 100

    # When
    ratio = country.calc_bank_equity_ratio()

    # Then
    assert ratio == 0.4


def test_calc_bank_equity_ratio_if_no_firms(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group1.equity = "B", 100
    group2.sector, group2.equity = "B", 100

    # When
    ratio = country.calc_bank_equity_ratio()

    # Then
    assert ratio == 1.0


def test_calc_median_firm_size(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group1.equity = "F", 50
    group2.sector, group2.equity = "F", 100

    # When
    median_size = country.calc_median_firm_size()

    # Then
    assert median_size == pytest.approx(50.0)


def test_calc_sector_size(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group2.sector = "X", "Y"

    # When
    sector_size = country.calc_sector_size("X")

    # Then
    assert sector_size == len(group1)


def test_calc_equity_range_for_any_sector(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group1.equity = "X", 100
    group2.sector, group2.equity = "Y", 100
    group2[-1].equity = 200

    # When
    range_ = country.calc_equity_range("Y")

    # Then
    assert range_ == (100, 200)


def test_calc_equity_range_if_empty_sector(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group1.equity = "X", 100
    group2.sector, group2.equity = "Y", 100

    # When
    range_ = country.calc_equity_range("Z")

    # Then
    assert range_ is None


def test_calc_phi_range_from_goods_market(country_with_two_groups):
    # Given
    market = Mock()
    country, *_ = country_with_two_groups
    country.spaces = {"goods_market": market}

    # When
    range_ = country.calc_phi_range("FNT")

    # Then
    assert range_ == market.calc_phi_range.return_value


def test_calc_phi_range_from_union(country_with_two_groups):
    # Given
    union = Mock()
    country, *_ = country_with_two_groups
    country.env = union

    # When
    range_ = country.calc_phi_range("FT")

    # Then
    assert range_ == union.calc_phi_range.return_value


def test_calc_price_range_from_goods_market(country_with_two_groups):
    # Given
    market = Mock()
    country, *_ = country_with_two_groups
    country.spaces = {"goods_market": market}

    # When
    range_ = country.calc_price_range("FNT")

    # Then
    assert range_ == market.calc_price_range.return_value


def test_calc_price_range_from_union(country_with_two_groups):
    # Given
    union = Mock()
    country, *_ = country_with_two_groups
    country.env = union

    # When
    range_ = country.calc_price_range("FT")

    # Then
    assert range_ == union.calc_price_range.return_value


def test_calc_sales_range_from_goods_market(country_with_two_groups):
    # Given
    market = Mock()
    country, *_ = country_with_two_groups
    country.spaces = {"goods_market": market}

    # When
    range_ = country.calc_sales_range("FNT")

    # Then
    assert range_ == market.calc_sales_range.return_value


def test_calc_sales_range_from_union(country_with_two_groups):
    # Given
    union = Mock()
    country, *_ = country_with_two_groups
    country.env = union

    # When
    range_ = country.calc_sales_range("FT")

    # Then
    assert range_ == union.calc_sales_range.return_value


def test_calc_wage_range_from_labor_market(country_with_two_groups):
    # Given
    market = Mock()
    country, *_ = country_with_two_groups
    country.spaces = {"labor_market": market}

    # When
    range_ = country.calc_wage_range("X")

    # Then
    assert range_ == market.calc_wage_range.return_value


# ---------------------------------------------------
# EQUITY INVESTMENT
# ----------------------------------------------------


@pytest.fixture
def before_transaction(country_with_two_groups):
    # Given
    country, *_ = country_with_two_groups
    country.transfer_stock = Mock()
    country.make_transaction = Mock()
    return country


def test_pay_public_transfers_calls_cash_transfer(before_transaction):
    # Given
    country = before_transaction
    citizen = Mock(id=1)
    auth = Mock(id=2)

    # When
    country.pay_public_transfers(auth, citizen, 10)

    # Then
    country.transfer_stock.assert_any_call("cash", auth.id, citizen.id, 10)


def test_pay_public_transfers_updates_accounts(before_transaction):
    # Given
    country = before_transaction
    citizen = Mock(id=1)
    auth = Mock(id=2)

    # When
    country.pay_public_transfers(auth, citizen, 10)

    # Then
    country.make_transaction.assert_any_call("public_transfers", 2, 1, 10)


@pytest.fixture
def country_with_company_and_founder(before_transaction):
    # Given
    company = Mock()
    founder = Mock(desired_investment=0, company_number=0)
    country = before_transaction
    country.graph.add_edge(company, founder, value=0)
    return country, company, founder


def test_fund_company_calls_cash_transfer(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.fund_company(company, founder, 100)

    # Then
    country.transfer_stock.assert_any_call("cash", founder.id, company.id, 100)


def test_fund_company_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.fund_company(company, founder, 100)

    # Then
    country.transfer_stock.assert_any_call("equities", company.id, founder.id, 100)


def test_fund_company_adds_graph_edge(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    graph = country.graph
    graph.remove_edge(company, founder)

    # When
    country.fund_company(company, founder, 100)

    # Then
    assert graph[company][founder]["value"] == 100


def test_fund_company_updates_graph_edge(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    country.graph.add_edge(company, founder, value=50)

    # When
    country.fund_company(company, founder, 100)

    # Then
    assert country.graph[company][founder]["value"] == 150


def test_fund_company_reduces_desired_investment(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    founder.desired_investment = 150

    # When
    country.fund_company(company, founder, 100)

    # Then
    assert founder.desired_investment == 50


def test_fund_company_increases_company_number(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    founder.company_number = 1

    # When
    country.fund_company(company, founder, 100)

    # Then
    assert founder.company_number == 2


# ---------------------------------------------------
#  DIVIDENDS AND TAXES
# ----------------------------------------------------


def test_pay_taxes_calls_cash_transfer(before_transaction):
    # Given
    payer, auth = Mock(), Mock()
    country = before_transaction
    country.fiscal_authority = auth

    # When
    country.pay_taxes(payer, 10)

    # Then
    country.transfer_stock.assert_any_call("cash", payer.id, auth.id, 10)


def test_pay_taxes_updates_accounts(before_transaction):
    # Given
    payer, auth = Mock(), Mock()
    country = before_transaction
    country.fiscal_authority = auth

    # When
    country.pay_taxes(payer, 10)

    # Then
    country.make_transaction.assert_any_call("taxes", payer.id, auth.id, 10)


def test_pay_dividends_calls_cash_transfer(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.pay_dividends(company, founder, 10)

    # Then
    country.transfer_stock.assert_any_call("cash", company.id, founder.id, 10)


def test_pay_dividends_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.pay_dividends(company, founder, 10)

    # Then
    country.make_transaction.assert_any_call("dividends", company.id, founder.id, 10)


def test_update_equity_share_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    source, target = company.id, founder.id

    # When
    country.update_equity_share(company, founder, 10)

    # Then
    country.transfer_stock.assert_any_call("equities", source, target, 10)
    country.make_transaction.assert_any_call("profit_transfers", source, target, 10)


def test_update_equity_share_updates_graph_edge(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.update_equity_share(company, founder, 10)

    # Then
    assert country.graph[company][founder]["value"] == 10


# ---------------------------------------------------
# TRANSFERS
# ----------------------------------------------------


def test_transfer_cb_profits_increases_govt_cash(before_transaction):
    # Given
    country = before_transaction
    country.monetary_authority = Mock(id=2)
    country.fiscal_authority = Mock(id=1)

    # When
    country.transfer_central_bank_profits(100)

    # Then
    country.transfer_stock.assert_any_call("cash", 2, 1, 100)


def test_transfer_profits_to_government(before_transaction):
    # Given
    country = before_transaction
    country.fiscal_authority = Mock(id=1)
    country.monetary_authority = Mock(id=2)

    # When
    country.transfer_central_bank_profits(100)

    # Then
    country.make_transaction.assert_any_call("profit_transfers", 2, 1, 100)


def test_transfer_residual_cash_calls_cash_transfer(before_transaction):
    # Given
    company, founder = Mock(), Mock()
    country = before_transaction

    # When
    country.transfer_residual_cash(company, founder, 100)

    # Then
    country.transfer_stock.assert_any_call("cash", company.id, founder.id, 100)


def test_transfer_residual_cash_of_company(before_transaction):
    # Given
    company, founder = Mock(), Mock()
    country = before_transaction

    # When
    country.transfer_residual_cash(company, founder, 100)

    # Then
    country.transfer_stock.assert_any_call("equities", founder.id, company.id, 100)


# ---------------------------------------------------
# CASH ADVANCE REQUEST / REPAYMENT
# ----------------------------------------------------


def test_request_advances_increases_company_cash(before_transaction):
    # Given
    country = before_transaction
    country.monetary_authority = Mock(id=1)
    company = Mock(id=2)

    # When
    country.request_advances(company, 100)

    # Then
    country.transfer_stock.assert_any_call("cash", 1, 2, 100)


def test_request_advances_updates_accounts(before_transaction):
    # Given
    country = before_transaction
    country.monetary_authority = Mock(id=1)
    company = Mock(id=2)

    # When
    country.request_advances(company, 100)

    # Then
    country.transfer_stock.assert_any_call("advances", 2, 1, 100)


def test_repay_advances_decreases_cash(before_transaction):
    # Given
    country = before_transaction
    country.monetary_authority = Mock(id=1)
    company = Mock(id=2)

    # When
    country.repay_advances(company, 100, 10)

    # Then
    country.transfer_stock.assert_any_call("cash", 2, 1, 110)


def test_repay_advances_updates_accounts(before_transaction):
    # Given
    country = before_transaction
    country.monetary_authority = Mock(id=1)
    company = Mock(id=2)

    # When
    country.repay_advances(company, 100, 10)

    # Then
    country.transfer_stock.assert_any_call("advances", 1, 2, 100)
    country.make_transaction.assert_any_call("adv_interests", 2, 1, 10)


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def country_before_update(country_with_two_groups):
    # Given
    country, *_ = country_with_two_groups
    country.spaces["goods_market"] = Mock()
    country.spaces["any_space"] = Mock()
    country.roles = {}
    country.gdp = 0
    return country


def test_update_state_updates_gdp(country_before_update):
    # Given
    country = country_before_update
    country.spaces["goods_market"].calc_gdp.return_value = 100

    # When
    country.update_state()

    # Then
    assert country.gdp == 100


def test_update_state_updates_inflation(country_before_update):
    # Given
    country = country_before_update
    country.spaces["goods_market"].calc_inflation.return_value = 0.2

    # When
    country.update_state()

    # Then
    assert country.inflation == 0.2


def test_update_state_updates_prob_failure(country_before_update):
    # Given
    default = Mock(defaulted=True)
    other = Mock(defaulted=False)
    other.name = default.name = "company"
    country = country_before_update
    country.roles[0] = default
    country.roles[1] = other

    # When
    country.update_state()

    # Then
    assert country.prob_failure == 0.5


def test_update_state_updates_each_subspace(country_before_update):
    # Given
    country = country_before_update

    # When
    country.update_state()

    # Then
    for subspace in country.spaces.values():
        subspace.update_state.assert_called_with()


@pytest.fixture
def country_with_defaults(country_with_roles):
    # Given
    companies = [Mock(defaulted=val) for val in [True, False]]
    citizens = [Mock(company_number=i) for i in range(1, 3)]
    country, roles = country_with_roles
    for company, citizen in zip(companies, citizens):
        company.name = "company"
        roles[company.agent.id] = company
        country.graph.add_edge(company, citizen)
    country.spaces = {n: Mock() for n in range(10)}
    country.remove_role = Mock()
    return country, companies, citizens


def test_clear_defaults_remove_defaulted_company(country_with_defaults):
    # Given
    country, companies, _ = country_with_defaults

    # When
    country.clear_defaults()

    # Then
    assert call(companies[0]) in country.remove_role.call_args_list
    assert call(companies[1]) not in country.remove_role.call_args_list
    assert country.remove_role.call_count == 1


def test_clear_defaults_reduces_company_number(country_with_defaults):
    # Given
    country, _, citizens = country_with_defaults

    # When
    country.clear_defaults()

    # Then
    assert citizens[0].company_number == 0
    assert citizens[1].company_number == 2


def test_clear_defaults_uses_spaces_method(country_with_defaults):
    # Given
    country, *_ = country_with_defaults

    # When
    country.clear_defaults()

    # Then
    for subspace in country.spaces.values():
        subspace.clear_defaults.assert_called_with()
