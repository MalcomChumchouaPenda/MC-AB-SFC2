from unittest.mock import Mock
import pytest
from agentpy import Model
from model.spaces.monetary_union import MonetaryUnion
from model.agents.household import Household
from model.agents.firm import Firm
from model.agents.bank import Bank


@pytest.fixture
def model(fake_model, make_dlist):
    # Given
    model = fake_model
    model.p.K = 1
    model.firms = make_dlist()
    model.banks = make_dlist()
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.build_space()
    return union


@pytest.fixture
def country(union):
    # Given
    country = union.spaces["country_0"]
    country.monetary_authority = Mock()
    return country


@pytest.fixture
def household(model):
    # Given
    household = Household(model)
    return household


@pytest.fixture
def before_allocation(country, household):
    # Given
    country.add_citizen(household)
    household.roles["depositor"] = Mock()


@pytest.mark.usefixtures("before_allocation")
def test_household_portfolio_allocation(country, household):
    # Given
    country.prob_failure = 0.0
    role = household.roles["depositor"]
    role.get_deposit_rate.return_value = 0.05
    household.p.lambda_ = 0.4
    household.disposable_income = 100
    household.expected_consumption = 50
    household.account["dividends"] = 2.5
    household.account["equities"] = 50
    household.account["deposits"] = 0
    household.account["cash"] = 0

    # When
    household.choose_portfolio_allocation()

    # Then
    assert household.desired_equity == pytest.approx(60.0)
    assert household.desired_deposits == pytest.approx(90.0)


@pytest.fixture
def founders(model):
    # Given
    model.p.cT = 0.6
    model.p.eta = 0.3
    model.p.initial_equity = 400
    founders = []
    for i in range(2):
        hh = Household(model)
        hh.roles["depositor"] = Mock()
        hh.desired_equity = 300 - i * 100
        founders.append(hh)
    return founders


@pytest.fixture
def before_investment(country, founders):
    # Given
    for founder in founders:
        role = country.add_citizen(founder)
        role.resid_equity = founder.desired_equity
        founder.account["cash"] = 400


@pytest.mark.usefixtures("before_investment")
def test_household_creates_new_firm(country, founders, model):
    # Given
    household1, household2 = founders
    citizen1 = household1.roles["citizen"]
    citizen2 = household2.roles["citizen"]
    firms = model.firms
    positions = country.positions

    # When
    household1.invest_equity()

    # Then
    assert len(firms) == 1
    assert isinstance(firms[0], Firm)
    assert household1.account["equities"] == 300
    assert household1.account["cash"] == 100
    assert household2.account["equities"] == 200
    assert household2.account["cash"] == 200
    assert country.get_stock("equities", firms[0].id) == -500
    assert country.get_stock("cash", firms[0].id) == 500
    assert country.graph[citizen1][positions[firms[0]]]["value"] == 300
    assert country.graph[citizen2][positions[firms[0]]]["value"] == 200


@pytest.mark.usefixtures("before_investment")
def test_household_creates_new_bank(country, founders, model):
    # Given
    household1, household2 = founders
    citizen1 = household1.roles["citizen"]
    citizen2 = household2.roles["citizen"]
    positions = country.positions
    banks = model.banks
    roles = country.roles
    roles.update({i: Mock(equity=100, sector="F", group="company") for i in range(5)})

    # # When
    household1.invest_equity()

    # Then
    assert len(banks) == 1
    assert isinstance(banks[0], Bank)
    assert household1.account["equities"] == 300
    assert household1.account["cash"] == 100
    assert household2.account["equities"] == 200
    assert household2.account["cash"] == 200
    assert country.get_stock("equities", banks[0].id) == -500
    assert country.get_stock("cash", banks[0].id) == 500
    assert country.graph[citizen1][positions[banks[0]]]["value"] == 300
    assert country.graph[citizen2][positions[banks[0]]]["value"] == 200


@pytest.mark.usefixtures("before_investment")
def test_household_makes_deposits(founders, model):
    # Given
    household1, household2 = founders
    citizen2 = household2.roles["citizen"]
    citizen2.resid_equity = household2.desired_equity = 0
    banks = model.banks
    firms = model.firms

    # When
    household1.invest_equity()

    # Then
    household1.roles["depositor"].make_deposits.assert_called_with(400)
    assert len(firms) == 0
    assert len(banks) == 0


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    return firm


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    return bank


@pytest.fixture
def before_distribution(country, firm, bank, household):
    # Given
    founder = country.add_citizen(household)
    company1 = country.add_company(firm, "FT")
    company2 = country.add_company(bank, "B")
    country.fund_company(company1, founder, 500)
    country.fund_company(company2, founder, 500)


@pytest.mark.usefixtures("before_distribution")
def test_firm_pay_dividends(firm, household):
    # Given
    household.account["cash"] = 0
    firm.account["cash"] = 1000
    firm.dividends_payable = 200

    # When
    firm.pay_dividends()

    # Then
    assert firm.dividends_payable == 0
    assert firm.account["dividends"] == -200
    assert firm.account["cash"] == 800
    assert household.account["cash"] == 200
    assert household.account["dividends"] == 200


@pytest.mark.usefixtures("before_distribution")
def test_bank_pay_dividends(bank, household):
    # Given
    household.account["cash"] = 0
    bank.account["cash"] = 500
    bank.dividends_payable = 100

    # When
    bank.pay_dividends()

    # Then
    assert bank.dividends_payable == 0
    assert bank.account["dividends"] == -100
    assert bank.account["cash"] == 400
    assert household.account["cash"] == 100
    assert household.account["dividends"] == 100


@pytest.mark.usefixtures("before_distribution")
def test_firm_update_net_worth(firm, household):
    # Given
    firm.net_worth = 1000
    firm.net_cash_flow = 500
    firm.taxes_payable = 100
    firm.dividends_payable = 200
    firm.account["equities"] = -1000
    household.account["equities"] = 1000

    # When
    firm.update_net_worth()

    # Then
    assert firm.net_worth == 1200
    assert firm.account["equities"] == -1200
    assert household.account["equities"] == 1200


@pytest.mark.usefixtures("before_distribution")
def test_bank_update_net_worth(bank, household):
    # Given
    bank.net_worth = 800
    bank.profit = 200
    bank.taxes_payable = 50
    bank.dividends_payable = 50
    bank.account["equities"] = -800
    household.account["equities"] = 800

    # When
    bank.update_net_worth()

    # Then
    assert bank.net_worth == 900
    assert bank.account["equities"] == -900
    assert household.account["equities"] == 900
