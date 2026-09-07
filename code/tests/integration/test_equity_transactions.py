import pytest
from unittest.mock import Mock
from agentpy import Model
from model.base import EcoAccount
from model.spaces.country import Country
from model.agents.household import Household
from model.agents.firm import Firm
from model.agents.bank import Bank


@pytest.fixture
def model():
    # Given
    model = Model()
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.setup()
    country.union = Mock()
    country.labor_market = Mock()
    country.deposit_market = Mock()
    country.good_market = Mock()
    country.monetary_authority = Mock()
    return country



@pytest.fixture
def founders(model):
    # Given
    model.p.cT = 0.6
    model.p.eta = 0.3
    model.p.initial_equity = 400
    founders = []
    for i in range(2):
        hh = Household(model)
        hh.setup()
        hh.roles["depositor"] = Mock()
        hh.account = EcoAccount(model)
        hh.account.setup()
        hh.account.stocks["cash"] = 400
        hh.desired_equity = 300 - i*100
        founders.append(hh)
    return founders


@pytest.fixture
def country_before_investment(country, founders):
    # Given
    for founder in founders:
        role = country.add_citizen(founder)
        role.resid_equity = founder.desired_equity
    def add_account(agent):
        agent.account = EcoAccount(country.model)
        agent.account.setup()
    country.union.add_account = add_account
    return country


def test_household_creates_new_firm(country_before_investment, founders):
    # Given
    household1, household2 = founders
    citizen1 = household1.roles["citizen"]
    citizen2 = household2.roles["citizen"]
    country = country_before_investment
    companies = country.companies

    # When
    household1.invest_equity()

    # Then
    assert len(companies) == 1
    assert isinstance(companies[0].agent, Firm)
    assert companies[0].account.stocks["equities"] == -500
    assert companies[0].account.stocks["cash"] == 500
    assert citizen1.account.stocks["equities"] == 300
    assert citizen1.account.stocks["cash"] == 100
    assert citizen2.account.stocks["equities"] == 200
    assert citizen2.account.stocks["cash"] == 200
    assert country.graph[citizen1][companies[0]]["value"] == 300
    assert country.graph[citizen2][companies[0]]["value"] == 200



def test_household_creates_new_bank(country_before_investment, founders):
    # Given
    household1, household2 = founders
    citizen1 = household1.roles["citizen"]
    citizen2 = household2.roles["citizen"]
    country = country_before_investment
    companies = country.companies
    companies.extend([Mock(equity=100, sector="F") for _ in range(5)])

    # # When
    household1.invest_equity()

    # Then
    assert len(companies) == 6
    assert isinstance(companies[-1].agent, Bank)
    assert companies[-1].account.stocks["equities"] == -500
    assert companies[-1].account.stocks["cash"] == 500
    assert citizen1.account.stocks["equities"] == 300
    assert citizen1.account.stocks["cash"] == 100
    assert citizen2.account.stocks["equities"] == 200
    assert citizen2.account.stocks["cash"] == 200
    assert country.graph[citizen1][companies[-1]]["value"] == 300
    assert country.graph[citizen2][companies[-1]]["value"] == 200


def test_household_makes_deposits_with_residual_cash(country_before_investment, founders):
    # Given
    household1, household2 = founders
    citizen2 = household2.roles["citizen"]
    citizen2.resid_equity = household2.desired_equity = 0
    country = country_before_investment
    companies = country.companies

    # When
    household1.invest_equity()

    # Then
    household1.roles["depositor"].make_deposits.assert_called_with(400)
    assert len(companies) == 0
    


    

@pytest.fixture
def household(model):
    # Given
    household = Household(model)
    household.setup()
    return household


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.setup()
    return firm


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    bank.setup()
    return bank

@pytest.fixture
def country_before_distribution(country, firm, bank, household):
    # Given
    def add_account(agent):
        agent.account = EcoAccount(country.model)
        agent.account.setup()
    country.union.add_account = add_account
    founder = country.add_citizen(household)
    company1 = country.add_company(firm, "FT")
    company2 = country.add_company(bank, "B")
    country.fund_company(company1, founder, 500)
    country.fund_company(company2, founder, 500)


@pytest.mark.usefixtures("country_before_distribution")
def test_firm_pay_dividends(firm, household):
    # Given
    household.account.stocks["cash"] = 0
    firm.account.stocks["cash"] = 1000
    firm.dividends_payable = 200

    # When
    firm.pay_dividends()

    # Then
    assert firm.dividends_payable == 0
    assert firm.account.flows["dividends"] == -200
    assert firm.account.stocks["cash"] == 800
    assert household.account.stocks["cash"] == 200
    assert household.account.flows["dividends"] == 200


@pytest.mark.usefixtures("country_before_distribution")
def test_bank_pay_dividends(bank, household):
    # Given
    household.account.stocks["cash"] = 0
    bank.account.stocks["cash"] = 500
    bank.dividends_payable = 100


    # When
    bank.pay_dividends()

    # Then
    assert bank.dividends_payable == 0
    assert bank.account.flows["dividends"] == -100
    assert bank.account.stocks["cash"] == 400
    assert household.account.stocks["cash"] == 100
    assert household.account.flows["dividends"] == 100
    
