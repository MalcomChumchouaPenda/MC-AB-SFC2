import pytest
from unittest.mock import Mock
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


FakeGoodMarket = Mock()
FakeLaborMarket = Mock()
FakeDepositMarket = Mock()


@pytest.fixture
def country_without_markets(monkeypatch, model):
    # Given
    monkeypatch.setattr("model.spaces.country.GoodsMarket", FakeGoodMarket)
    monkeypatch.setattr("model.spaces.country.LaborMarket", FakeLaborMarket)
    monkeypatch.setattr("model.spaces.country.DepositMarket", FakeDepositMarket)
    monkeypatch.setattr(Country, "add_space", Mock())
    country = Country(model)
    country.pos = 2
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


FakeMonetaryAuth = Mock()
FakeFiscalAuth = Mock()
FakeCitizen = Mock()
FakeCompany = Mock()


@pytest.fixture
def country_without_roles(model, monkeypatch):
    # Given
    monkeypatch.setattr("model.spaces.country.MonetaryAuthority", FakeMonetaryAuth)
    monkeypatch.setattr("model.spaces.country.FiscalAuthority", FakeFiscalAuth)
    monkeypatch.setattr("model.spaces.country.Citizen", FakeCitizen)
    monkeypatch.setattr("model.spaces.country.Company", FakeCompany)
    country = Country(model)
    country.add_role = Mock()
    country.env = Mock()
    country.spaces["goods_market"] = Mock()
    country.spaces["labor_market"] = Mock()
    country.spaces["deposit_market"] = Mock()
    return country


def test_add_household_add_citizen_role(country_without_roles):
    # Given
    household = Mock()
    country = country_without_roles

    # When
    country.add_household(household)

    # Then
    country.add_role.assert_called_with(FakeCitizen, household)


def test_add_household_places_agent_into_goods_market(country_without_roles):
    # Given
    household = Mock(country_pos=1)
    country = country_without_roles
    market = country.spaces["goods_market"]

    # When
    country.add_household(household)

    # Then
    market.add_household.assert_called_with(household)


def test_add_household_places_agent_into_labor_market(country_without_roles):
    # Given
    household = Mock(country_pos=1)
    country = country_without_roles
    market = country.spaces["labor_market"]

    # When
    country.add_household(household)

    # Then
    market.add_household.assert_called_with(household)


def test_add_household_places_agent_into_deposit_market(country_without_roles):
    # Given
    household = Mock(country_pos=1)
    country = country_without_roles
    market = country.spaces["deposit_market"]

    # When
    country.add_household(household)

    # Then
    market.add_household.assert_called_with(household)


@pytest.mark.parametrize("tradable", [True, False])
def test_add_firm_add_company_role(country_without_roles, tradable):
    # Given
    firm = Mock(tradable=tradable)
    country = country_without_roles

    # When
    country.add_firm(firm)

    # Then
    country.add_role.assert_called_with(FakeCompany, firm)


@pytest.mark.parametrize("tradable, sector", [(True, "FT"), (False, "FNT")])
def test_add_firm_sets_company_sector(country_without_roles, tradable, sector):
    # Given
    role = Mock()
    firm = Mock(tradable=tradable)
    country = country_without_roles
    country.add_role.return_value = role

    # When
    country.add_firm(firm)

    # Then
    assert role.sector == sector


def test_add_firm_in_goods_market_if_not_tradable(country_without_roles):
    # Given
    firm = Mock(tradable=False)
    country = country_without_roles
    market = country.spaces["goods_market"]

    # When
    country.add_firm(firm)

    # Then
    market.add_firm.assert_called_with(firm)


def test_dont_add_firm_into_goods_market_if_tradable(country_without_roles):
    # Given
    firm = Mock(tradable=True)
    country = country_without_roles
    market = country.spaces["goods_market"]

    # When
    country.add_firm(firm)

    # Then
    market.add_firm.assert_not_called()


@pytest.mark.parametrize("tradable", [True, False])
def test_add_firm_into_deposit_market(country_without_roles, tradable):
    # Given
    firm = Mock(tradable=tradable)
    country = country_without_roles
    market = country.spaces["deposit_market"]

    # When
    country.add_firm(firm)

    # Then
    market.add_firm.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_add_firm_into_labor_market_if_domestic(country_without_roles, tradable):
    # Given
    country = country_without_roles
    market = country.spaces["labor_market"]
    firm = Mock(tradable=tradable, country_pos=country.pos)

    # When
    country.add_firm(firm)

    # Then
    market.add_firm.assert_called_with(firm)


def test_add_bank_add_company_role(country_without_roles):
    # Given
    bank = Mock()
    country = country_without_roles

    # When
    country.add_bank(bank)

    # Then
    country.add_role.assert_called_with(FakeCompany, bank)


def test_add_bank_sets_company_sector(country_without_roles):
    # Given
    role = Mock()
    bank = Mock()
    country = country_without_roles
    country.add_role.return_value = role

    # When
    country.add_bank(bank)

    # Then
    assert role.sector == "B"


def test_add_bank_in_deposit_market_if_not_tradable(country_without_roles):
    # Given
    bank = Mock()
    country = country_without_roles
    market = country.spaces["deposit_market"]

    # When
    country.add_bank(bank)

    # Then
    market.add_bank.assert_called_with(bank)


def test_add_government_add_fiscal_authority_role(country_without_roles):
    # Given
    govt = Mock()
    country = country_without_roles

    # When
    country.add_government(govt)

    # Then
    country.add_role.assert_called_with(FakeFiscalAuth, govt)


def test_add_government_sets_fiscal_authority(country_without_roles):
    # Given
    role = Mock()
    govt = Mock()
    country = country_without_roles
    country.add_role.return_value = role

    # When
    country.add_government(govt)

    # Then
    assert country.fiscal_authority == role


def test_add_government_into_deposit_market(country_without_roles):
    # Given
    govt = Mock(country_pos=1)
    country = country_without_roles
    market = country.spaces["deposit_market"]

    # When
    country.add_government(govt)

    # Then
    market.add_government.assert_called_with(govt)


def test_add_central_bank_add_monetary_authority_role(country_without_roles):
    # Given
    cb = Mock()
    country = country_without_roles

    # When
    country.add_central_bank(cb)

    # Then
    country.add_role.assert_called_with(FakeMonetaryAuth, cb)


def test_add_central_bank_sets_monetary_authority(country_without_roles):
    # Given
    cb = Mock()
    role = Mock()
    country = country_without_roles
    country.add_role.return_value = role

    # When
    country.add_central_bank(cb)

    # Then
    assert country.monetary_authority is role


# ---------------------------------------------------
# CURRENT INDICATORS
# ----------------------------------------------------


@pytest.fixture
def country_with_roles(country_without_roles):
    # Given
    roles = {}
    country = country_without_roles
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


def test_calc_sector_equity_range_for_any_sector(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group1.equity = "X", 100
    group2.sector, group2.equity = "Y", 100
    group2[-1].equity = 200

    # When
    range_ = country.calc_sector_equity_range("Y")

    # Then
    assert range_ == (100, 200)


def test_calc_sector_equity_range_if_empty_sector(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group1.equity = "X", 100
    group2.sector, group2.equity = "Y", 100

    # When
    range_ = country.calc_sector_equity_range("Z")

    # Then
    assert range_ is None


# ---------------------------------------------------
# EQUITY INVESTMENT
# ----------------------------------------------------


@pytest.fixture
def country_before_transaction(country_without_roles):
    # Given
    country = country_without_roles
    country.transfer_stock = Mock()
    country.make_transaction = Mock()
    return country


def test_pay_public_transfers_updates_accounts(country_before_transaction):
    # Given
    country = country_before_transaction
    citizen = Mock(id=1)
    auth = Mock(id=2)

    # When
    country.pay_public_transfers(auth, citizen, 10)

    # Then
    country.transfer_stock.assert_any_call("cash", 2, 1, 10)
    country.make_transaction.assert_any_call("public_transfers", 2, 1, 10)


@pytest.fixture
def country_with_company_and_founder(country_before_transaction):
    # Given
    company = Mock()
    founder = Mock(resid_equity=0, company_number=0)
    country = country_before_transaction
    country.graph.add_edge(company, founder, value=0)
    return country, company, founder


def test_fund_company_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.fund_company(company, founder, 100)

    # Then
    country.transfer_stock.assert_any_call("cash", founder.id, company.id, 100)
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


def test_fund_company_reduces_resid_equity(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    founder.resid_equity = 150

    # When
    country.fund_company(company, founder, 100)

    # Then
    assert founder.resid_equity == 50


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


def test_pay_taxes_updates_accounts(country_before_transaction):
    # Given
    payer, auth = Mock(), Mock()
    country = country_before_transaction
    country.fiscal_authority = auth

    # When
    country.pay_taxes(payer, 10)

    # Then
    country.transfer_stock.assert_any_call("cash", payer.id, auth.id, 10)
    country.make_transaction.assert_any_call("taxes", payer.id, auth.id, 10)


def test_pay_dividends_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.pay_dividends(company, founder, 10)

    # Then
    country.transfer_stock.assert_any_call("cash", company.id, founder.id, 10)
    country.make_transaction.assert_any_call("dividends", company.id, founder.id, 10)


def test_update_equity_share_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.update_equity_share(company, founder, -10)

    # Then
    country.transfer_stock.assert_any_call("equities", company.id, founder.id, -10)
    country.make_transaction.assert_any_call(
        "profit_transfers", company.id, founder.id, -10
    )


def test_update_equity_share_updates_graph_edge(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.update_equity_share(company, founder, -10)

    # Then
    assert country.graph[company][founder]["value"] == -10


# ---------------------------------------------------
# TRANSFERS
# ----------------------------------------------------


def test_transfer_profits_to_government(country_before_transaction):
    # Given
    country = country_before_transaction
    country.fiscal_authority = Mock(id=1)
    country.monetary_authority = Mock(id=2)

    # When
    country.transfer_central_bank_profits(100)

    # Then
    country.transfer_stock.assert_any_call("cash", 2, 1, 100)
    country.make_transaction.assert_any_call("profit_transfers", 2, 1, 100)


def test_transfer_residual_cash_of_company(country_before_transaction):
    # Given
    company, founder = Mock(), Mock()
    country = country_before_transaction

    # When
    country.transfer_residual_cash(company, founder, 100)

    # Then
    country.transfer_stock.assert_any_call("cash", company.id, founder.id, 100)
    country.transfer_stock.assert_any_call("equities", founder.id, company.id, 100)


# ---------------------------------------------------
# CASH ADVANCE REQUEST / REPAYMENT
# ----------------------------------------------------


def test_request_advances_updates_accounts(country_before_transaction):
    # Given
    country = country_before_transaction
    country.monetary_authority = Mock(id=1)
    company = Mock(id=2)

    # When
    country.request_advances(company, 100)

    # Then
    country.transfer_stock.assert_any_call("cash", 1, 2, 100)
    country.transfer_stock.assert_any_call("advances", 2, 1, 100)


def test_repay_advances_updates_accounts(country_before_transaction):
    # Given
    country = country_before_transaction
    country.monetary_authority = Mock(id=1)
    company = Mock(id=2)

    # When
    country.repay_advances(company, 100, 10)

    # Then
    country.transfer_stock.assert_any_call("cash", 2, 1, 110)
    country.transfer_stock.assert_any_call("advances", 1, 2, 100)
    country.make_transaction.assert_any_call("adv_interests", 2, 1, 10)


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def country_before_update(country_without_roles):
    # Given
    country = country_without_roles
    country.spaces["goods_market"] = Mock()
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
