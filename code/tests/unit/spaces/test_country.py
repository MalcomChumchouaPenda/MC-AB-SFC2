import pytest
from agentpy import AgentDList
from unittest.mock import Mock
from model.spaces.country import Country

# ---------------------------------------------------
# ARCHITECTURE TESTS
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


# ---------------------------------------------------
# ROLES SET/REF TESTS
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


# ---------------------------------------------------
# SPACES SET/REF TESTS
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
# DYNAMIC STATE TESTS
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
# ROLES MANAGEMENT TESTS
# ----------------------------------------------------


class FakeCitizen(Mock):
    pass


@pytest.fixture
def country_without_citizens(monkeypatch, country_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.country.Citizen", FakeCitizen)
    country = country_before_setup
    country.add_role = Mock()
    country.union = Mock()
    country.citizens = []
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



class FakeCompany(Mock):
    pass


@pytest.fixture
def country_without_companies(monkeypatch, country_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.country.Company", FakeCompany)
    country = country_before_setup
    country.add_role = Mock()
    country.union = Mock()
    country.companies = []
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



# ---------------------------------------------------
# EQUITY INVESTMENT AND DIVIDENDS
# ----------------------------------------------------


@pytest.fixture
def country_with_company_and_founder(country_before_setup):
    # Given
    company, founder = Mock(), Mock()
    country = country_before_setup
    country.graph.add_edge(company, founder, share=0)
    return country, company, founder


def test_fund_company_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.fund_company(company, founder, 100)

    # Then
    company.account.credit_stock("equities", 100)
    company.account.credit_stock("cash", 100)
    founder.account.debit_stock("equities", 100)
    founder.account.debit_stock("cash", 100)


def test_fund_company_adds_graph_edge(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    graph = country.graph

    # When
    country.fund_company(company, founder, 100)

    # Then
    assert graph[company][founder]["share"] == 100


def test_fund_company_updates_graph_edge(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    country.graph.add_edge(company, founder, share=50)

    # When
    country.fund_company(company, founder, 100)

    # Then
    assert country.graph[company][founder]["share"] == 150


def test_pay_dividends_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.pay_dividends(company, founder, 10)

    # Then
    company.account.debit_flow("dividends", 10)
    company.account.debit_flow("cash", 10)
    founder.account.credit_flow("dividends", 10)
    founder.account.credit_flow("cash", 10)


# ---------------------------------------------------
# FIRM CREATION TESTS
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
    country.good_market.add_supplier.assert_not_called()


def test_create_non_trad_firm_in_goods_market(country_before_creation, share):
    # Given
    firm = Mock()
    country = country_before_creation

    # When
    country.create_firm(firm, [share], tradable=False)

    # Then
    country.good_market.add_supplier.assert_called_with(firm)


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
# BANK CREATION TESTS
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
