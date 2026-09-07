import pytest
from agentpy import AgentDList
from unittest.mock import Mock
from model.spaces.country import Country

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from model.base import EcoSpace

    # Assert
    assert issubclass(Country, EcoSpace)


@pytest.fixture
def country_before_setup():
    # Given
    model = Mock()
    country = Country(model)
    return country


def test_has_monetary_union_ref(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.union is None


def test_has_inflation(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.inflation == 0


def test_has_gdp(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.gdp == 0


def test_has_prob_failure(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.prob_failure == 0


def test_has_tax_rate(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.tax_rate == 0


# ---------------------------------------------------
# ROLES
# ----------------------------------------------------


def test_has_fiscal_authority_ref(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.fiscal_authority is None


def test_has_monetary_authority_ref(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.monetary_authority is None


def test_has_citizens_list(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert isinstance(country.citizens, AgentDList)


def test_has_companies_list(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert isinstance(country.companies, AgentDList)


FakeAuthority1 = Mock()
FakeAuthority2 = Mock()


@pytest.fixture
def country_without_authorities(monkeypatch, country_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.country.MonetaryAuthority", FakeAuthority1)
    monkeypatch.setattr("model.spaces.country.FiscalAuthority", FakeAuthority2)
    country = country_before_setup
    country.add_role = Mock()
    country.union = Mock()
    return country


def test_add_monetary_authority_add_appropriate_role(country_without_authorities):
    # Given
    cb = Mock()
    country = country_without_authorities

    # When
    role = country.add_monetary_authority(cb)

    # Then
    country.add_role.assert_called_with(FakeAuthority1, cb, "monetary_authority")
    assert role == country.add_role.return_value


def test_add_monetary_authority_registers_authority(country_without_authorities):
    # Given
    cb = Mock()
    country = country_without_authorities

    # When
    role = country.add_monetary_authority(cb)

    # Then
    assert country.monetary_authority is role


def test_add_monetary_authority_add_account(country_without_authorities):
    # Given
    country = country_without_authorities
    union = country.union
    cb = Mock()

    # When
    country.add_monetary_authority(cb)

    # Then
    union.add_account.assert_called_with(cb)


def test_add_fiscal_authority_add_appropriate_role(country_without_authorities):
    # Given
    govt = Mock()
    country = country_without_authorities

    # When
    role = country.add_fiscal_authority(govt)

    # Then
    country.add_role.assert_called_with(FakeAuthority2, govt, "fiscal_authority")
    assert role == country.add_role.return_value


def test_add_fiscal_authority_registers_authority(country_without_authorities):
    # Given
    govt = Mock()
    country = country_without_authorities

    # When
    role = country.add_fiscal_authority(govt)

    # Then
    assert country.fiscal_authority is role


def test_add_fiscal_authority_add_account(country_without_authorities):
    # Given
    country = country_without_authorities
    union = country.union
    govt = Mock()

    # When
    country.add_fiscal_authority(govt)

    # Then
    union.add_account.assert_called_with(govt)


FakeCitizen = Mock()


@pytest.fixture
def country_without_citizens(monkeypatch, country_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.country.Citizen", FakeCitizen)
    country = country_before_setup
    country.add_role = Mock()
    country.citizens = []
    country.union = Mock()
    country.monetary_authority = Mock()
    return country


def test_add_citizen_add_appropriate_role(country_without_citizens):
    # Given
    household = Mock()
    country = country_without_citizens

    # When
    role = country.add_citizen(household)

    # Then
    country.add_role.assert_called_with(FakeCitizen, household, "citizen")
    assert role == country.add_role.return_value


def test_add_citizen_registers_citizen(country_without_citizens):
    # Given
    household = Mock()
    country = country_without_citizens

    # When
    role = country.add_citizen(household)

    # Then
    assert country.citizens == [role]


def test_add_citizen_add_account(country_without_citizens):
    # Given
    country = country_without_citizens
    union = country.union
    household = Mock()

    # When
    country.add_citizen(household)

    # Then
    union.add_account.assert_called_with(household)


def test_add_citizen_links_to_cb_account(country_without_citizens):
    # Given
    country = country_without_citizens
    authority = country.monetary_authority
    household = Mock()

    # When
    country.add_citizen(household)

    # Then
    assert household.cb_account is authority.account


FakeCompany = Mock()


@pytest.fixture
def country_without_companies(monkeypatch, country_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.country.Company", FakeCompany)
    country = country_before_setup
    country.add_role = Mock()
    country.union = Mock()
    country.companies = []
    country.monetary_authority = Mock()
    return country


def test_add_company_add_appropriate_role(country_without_companies):
    # Given
    agent = Mock()
    country = country_without_companies

    # When
    role = country.add_company(agent, sector="X")

    # Then
    country.add_role.assert_called_with(FakeCompany, agent, "company")
    assert role == country.add_role.return_value


def test_add_company_register_company(country_without_companies):
    # Given
    agent = Mock()
    country = country_without_companies

    # When
    role = country.add_company(agent, sector="X")

    # Then
    assert country.companies == [role]


def test_add_company_register_sector(country_without_companies):
    # Given
    agent = Mock()
    country = country_without_companies

    # When
    role = country.add_company(agent, sector="X")

    # Then
    assert role.sector == "X"


def test_add_company_add_account(country_without_companies):
    # Given
    country = country_without_companies
    union = country.union
    agent = Mock()

    # When
    country.add_company(agent, sector="X")

    # Then
    union.add_account.assert_called_with(agent)


def test_add_company_links_to_cb_account(country_without_companies):
    # Given
    country = country_without_companies
    authority = country.monetary_authority
    agent = Mock()

    # When
    country.add_company(agent, sector="X")

    # Then
    assert agent.cb_account is authority.account


# ---------------------------------------------------
# SUB OR ROOT SPACES
# ----------------------------------------------------


def test_has_monetary_union_ref(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.union is None


def test_has_good_market_ref(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.good_market is None


def test_has_labor_market_ref(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.labor_market is None


def test_has_deposit_market_ref(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.deposit_market is None


# ---------------------------------------------------
# LAG INDICATORS
# ----------------------------------------------------


def test_has_inflation_prop(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.inflation == 0.0


def test_has_gdp_prop(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.gdp == 0


def test_has_prob_failure_prop(country_before_setup):
    # Given
    country = country_before_setup

    # When
    country.setup()

    # Then
    assert country.prob_failure == 0.0


# ---------------------------------------------------
# CURRENT INDICATORS
# ----------------------------------------------------


@pytest.fixture
def country_with_companies(country_before_setup, make_dlist):
    # Given
    companies = make_dlist()
    country = country_before_setup
    country.companies = companies
    return country, companies


def test_calc_bank_number_ratio(country_with_companies):
    # Given
    country, companies = country_with_companies
    bank_sector = [Mock(sector="B") for _ in range(2)]
    firm_sector = [Mock(sector="F") for _ in range(10)]
    companies.extend(bank_sector + firm_sector)

    # When
    ratio = country.calc_bank_number_ratio()

    # Then
    assert ratio == 0.2


def test_calc_bank_number_ratio_if_no_firms(country_with_companies):
    # Given
    country, companies = country_with_companies
    bank_sector = [Mock(sector="B") for _ in range(2)]
    companies.extend(bank_sector)

    # When
    ratio = country.calc_bank_number_ratio()

    # Then
    assert ratio == 1.0


def test_calc_bank_equity_ratio(country_with_companies):
    # Given
    country, companies = country_with_companies
    bank_sector = [Mock(sector="B", equity=100) for _ in range(2)]
    firm_sector = [Mock(sector="F", equity=50) for _ in range(10)]
    companies.extend(bank_sector + firm_sector)

    # When
    ratio = country.calc_bank_equity_ratio()

    # Then
    assert ratio == 0.4


def test_calc_bank_equity_ratio_if_no_firms(country_with_companies):
    # Given
    country, companies = country_with_companies
    bank_sector = [Mock(sector="B", equity=100) for _ in range(2)]
    companies.extend(bank_sector)

    # When
    ratio = country.calc_bank_equity_ratio()

    # Then
    assert ratio == 1.0


def test_calc_sector_equity_range_for_any_sector(country_with_companies):
    # Given
    country, companies = country_with_companies
    target_companies = [Mock(sector="X", equity=100 * i) for i in range(2, 5)]
    other_companies = [Mock(sector="Y", equity=100 * i) for i in range(1, 6)]
    companies.extend(target_companies + other_companies)

    # When
    range_ = country.calc_sector_equity_range("X")

    # Then
    assert range_ == (200, 400)


def test_calc_sector_equity_range_if_empty_sector(country_with_companies):
    # Given
    country, companies = country_with_companies
    companies.extend([Mock(sector="Y", equity=100)])

    # When
    range_ = country.calc_sector_equity_range("X")

    # Then
    assert range_ is None


# ---------------------------------------------------
# EQUITY INVESTMENT
# ----------------------------------------------------


@pytest.fixture
def country_with_citizens(country_before_setup, make_dlist):
    # Given
    citizens = make_dlist([Mock(resid_equity=100) for _ in range(2)])
    country = country_before_setup
    country.citizens = citizens
    return country, citizens


def test_find_investors_with_positive_residual_equity(country_with_citizens):
    # Given
    country, citizens = country_with_citizens
    citizens[0].resid_equity = 0
    eligible = citizens[1]

    # When
    investors = country.find_investors()

    # Then
    assert investors == [eligible]


def test_find_investors_excludes_initiator(country_with_citizens):
    # Given
    country, citizens = country_with_citizens
    initiator = citizens[0]
    eligible = citizens[1]

    # When
    investors = country.find_investors(initiator=initiator)

    # Then
    assert investors == [eligible]


@pytest.fixture
def country_with_company_and_founder(country_before_setup):
    # Given
    company = Mock()
    founder = Mock(resid_equity=0)
    country = country_before_setup
    country.graph.add_edge(company, founder, value=0)
    return country, company, founder


def test_fund_company_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.fund_company(company, founder, 100)

    # Then
    company.debit_stock.assert_any_call("equities", 100)
    company.credit_stock.assert_any_call("cash", 100)
    founder.credit_stock.assert_any_call("equities", 100)
    founder.debit_stock.assert_any_call("cash", 100)


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


# ---------------------------------------------------
#  DIVIDENDS AND TAXES
# ----------------------------------------------------


def test_find_equity_shares(country_with_company_and_founder):
    # Given
    other = Mock()
    country, company, founder = country_with_company_and_founder
    country.graph.add_edge(company, founder, value=60)
    country.graph.add_edge(other, founder, value=40)

    # When
    found = country.find_equity_shares(company)

    # Assert
    assert found == [{"founder": founder, "value": 60}]


def test_pay_dividends_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.pay_dividends(company, founder, 10)

    # Then
    company.debit_flow.assert_any_call("dividends", 10)
    company.debit_stock.assert_any_call("cash", 10)
    founder.credit_flow.assert_any_call("dividends", 10)
    founder.credit_stock.assert_any_call("cash", 10)


def test_pay_taxes_updates_accounts(country_before_setup):
    # Given
    payer, authority = Mock(), Mock()
    country = country_before_setup
    country.fiscal_authority = authority

    # When
    country.pay_taxes(payer, 10)

    # Then
    payer.debit_flow.assert_any_call("taxes", 10)
    payer.debit_stock.assert_any_call("cash", 10)
    authority.credit_flow.assert_any_call("taxes", 10)
    authority.credit_stock.assert_any_call("cash", 10)


# ---------------------------------------------------
# FIRM CREATION
# ----------------------------------------------------


@pytest.fixture
def country_before_creation(country_before_setup):
    # Given
    country = country_before_setup
    country.add_company = Mock()
    country.fund_company = Mock()
    country.union = Mock()
    country.good_market = Mock()
    country.labor_market = Mock()
    country.deposit_market = Mock()
    return country


@pytest.fixture
def share():
    founder = Mock(resid_equity=10)
    return {"founder": founder, "amount": 5}


@pytest.mark.parametrize("trad, sector", [(True, "FT"), (False, "FNT")])
def test_create_firm_add_and_fund_company(country_before_creation, share, trad, sector):
    # Given
    firm = Mock()
    company = Mock()
    country = country_before_creation
    country.add_company.return_value = company

    # When
    country.create_firm(firm, [share], tradable=trad)

    # Then
    country.add_company.assert_called_with(firm, sector=sector)
    country.fund_company.assert_called_with(company, share["founder"], 5)


def test_dont_create_trad_firm_in_goods_market(country_before_creation, share):
    # Given
    firm = Mock()
    country = country_before_creation

    # When
    country.create_firm(firm, [share], tradable=True)

    # Then
    country.good_market.add_producer.assert_not_called()


def test_create_non_trad_firm_in_goods_market(country_before_creation, share):
    # Given
    firm = Mock()
    country = country_before_creation

    # When
    country.create_firm(firm, [share], tradable=False)

    # Then
    country.good_market.add_producer.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_employer_role(country_before_creation, share, tradable):
    # Given
    firm = Mock()
    country = country_before_creation

    # When
    country.create_firm(firm, [share], tradable=tradable)

    # Then
    country.labor_market.add_employer.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_depositor_role(country_before_creation, share, tradable):
    # Given
    firm = Mock()
    country = country_before_creation

    # When
    country.create_firm(firm, [share], tradable=tradable)

    # Then
    country.deposit_market.add_depositor.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_place_firm_in_union(country_before_creation, share, tradable):
    # Given
    firm = Mock()
    country = country_before_creation

    # When
    country.create_firm(firm, [share], tradable=tradable)

    # Then
    country.union.place_firm.assert_called_with(firm, tradable=tradable)


# ---------------------------------------------------
# BANK CREATION
# ----------------------------------------------------


def test_create_bank_add_and_fund_company(country_before_creation, share):
    # Given
    bank = Mock()
    company = Mock()
    country = country_before_creation
    country.add_company.return_value = company

    # When
    country.create_bank(bank, [share])

    # Then
    country.add_company.assert_called_with(bank, sector="B")
    country.fund_company.assert_called_with(company, share["founder"], 5)


def test_create_bank_add_bank_role(country_before_creation, share):
    # Given
    bank = Mock()
    country = country_before_creation

    # When
    country.create_bank(bank, [share])

    # Then
    country.deposit_market.add_bank.assert_called_with(bank)


def test_create_bank_place_bank_in_union(country_before_creation, share):
    # Given
    bank = Mock()
    country = country_before_creation

    # When
    country.create_bank(bank, [share])

    # Then
    country.union.place_bank.assert_called_with(bank)


# ---------------------------------------------------
# TRANSFER PROFITS
# ----------------------------------------------------

def test_transfer_profits_to_government(country_before_setup):
    # Given
    fiscal_auth, monetary_auth = Mock(), Mock()
    country = country_before_setup
    country.fiscal_authority = fiscal_auth
    country.monetary_authority = monetary_auth

    # When
    country.transfer_central_bank_profits(100)

    # Then
    fiscal_auth.credit_stock.assert_any_call("cash", 100)
    fiscal_auth.credit_flow.assert_any_call("profit_transfers", 100)
    monetary_auth.debit_stock.assert_any_call("cash", 100)
    monetary_auth.debit_flow.assert_any_call("profit_transfers", 100)


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def country_before_update(country_before_setup, make_dlist):
    # Given
    country = country_before_setup
    country.good_market = Mock()
    country.gdp = 0
    country.companies = make_dlist()
    return country


def test_update_state_updates_gdp(country_before_update):
    # Given
    country = country_before_update
    country.good_market.calc_gdp.return_value = 100

    # When
    country.update_state()

    # Then
    assert country.gdp == 100


def test_update_state_updates_inflation(country_before_update):
    # Given
    country = country_before_update
    country.good_market.calc_inflation.return_value = 0.2

    # When
    country.update_state()

    # Then
    assert country.inflation == 0.2


def test_update_state_updates_prob_failure(country_before_update):
    # Given
    defaults = [Mock(defaulted=True) for _ in range(5)]
    others = [Mock(defaulted=False) for _ in range(5)]
    country = country_before_update
    country.companies.extend(defaults + others)

    # When
    country.update_state()

    # Then
    assert country.prob_failure == 0.5
