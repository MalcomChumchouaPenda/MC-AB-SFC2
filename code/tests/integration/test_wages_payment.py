import pytest
from model.spaces.country import Country
from model.agents.household import Household
from model.agents.firm import Firm


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.initial_wage = 0.0
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.create_markets()
    return country


@pytest.fixture
def market(country):
    # Given
    market = country.spaces["labor_market"]
    return market


@pytest.fixture
def firm(model, country):
    # Given
    firm = Firm(model)
    firm.country_pos = country.pos
    country.add_agents([firm])
    return firm


@pytest.fixture
def households(model, country):
    # Given
    households = []
    for _ in range(2):
        household = Household(model)
        household.country_pos = country.pos
        country.add_agents([household])
        households.append(household)
    return households


@pytest.fixture
def before_payment(market, firm, households):
    # Given
    employer = firm.roles["employer"]
    employer.wage = 10.0
    for household in households:
        worker = household.roles["worker"]
        market.hire_worker(worker, employer, 1.0)


@pytest.mark.usefixtures("before_payment")
def test_increases_wages_from_firm(firm, households):
    # When
    firm.pay_wages()

    # Then
    assert firm.account["wages"] == -20.0
    assert households[0].account["wages"] == 10.0
    assert households[1].account["wages"] == 10.0


@pytest.mark.usefixtures("before_payment")
def test_transfers_cash_from_firm_to_household(firm, households, country):
    # Given
    cash = country.cash

    # When
    firm.pay_wages()

    # Then
    assert cash[firm.id].amount == -20.0
    assert cash[households[0].id].amount == 10.0
    assert cash[households[1].id].amount == 10.0
