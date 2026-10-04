import pytest
from model.spaces.labor_market import LaborMarket
from model.agents.household import Household
from model.agents.firm import Firm


@pytest.fixture
def market(fake_model):
    # Given
    market = LaborMarket(fake_model)
    return market


@pytest.fixture
def firm(fake_model, market):
    # Given
    firm = Firm(fake_model)
    market.add_firm(firm)
    employer = firm.roles["employer"]
    employer.wage = 10.0
    return firm


@pytest.fixture
def households(fake_model, market, firm):
    # Given
    households = []
    employer = firm.roles["employer"]
    for _ in range(2):
        household = Household(fake_model)
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
