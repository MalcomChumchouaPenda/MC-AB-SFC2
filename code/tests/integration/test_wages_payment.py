import pytest
from model.spaces.labor_market import LaborMarket
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
def market(model):
    # Given
    market = LaborMarket(model)
    return market


@pytest.fixture
def firm(model, market):
    # Given
    firm = Firm(model)
    market.add_firm(firm)
    employer = firm.roles["employer"]
    employer.wage = 10.0
    return firm


@pytest.fixture
def households(model, market, firm):
    # Given
    households = []
    employer = firm.roles["employer"]
    for _ in range(2):
        household = Household(model)
        market.add_household(household)
        worker = household.roles["worker"]
        market.hire_worker(worker, employer, 1.0)
        households.append(household)
    return households


def test_increases_wages_from_firm(firm, households):
    # When
    firm.pay_wages()

    # Then
    assert firm.account["wages"] == -20.0
    assert households[0].account["wages"] == 10.0
    assert households[1].account["wages"] == 10.0


def test_transfers_cash_from_firm_to_household(firm, households):
    # When
    firm.pay_wages()

    # Then
    assert firm.account["cash"] == -20.0
    assert households[0].account["cash"] == 10.0
    assert households[1].account["cash"] == 10.0
