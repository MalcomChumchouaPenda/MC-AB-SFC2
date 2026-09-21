import pytest
from unittest.mock import Mock
from agentpy import Model
from model.spaces.monetary_union import MonetaryUnion
from model.agents.household import Household
from model.agents.firm import Firm
from model.agents.bank import Bank


@pytest.fixture
def model():
    # Given
    model = Model()
    model.p.K = 1
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.setup()
    union.monetary_authority = Mock()
    union.countries[0].monetary_authority = Mock()
    return union


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
def country_with_bank_and_founders(union, bank, model):
    # Given
    country = union.countries[0]
    founders = []
    shares = []
    for _ in range(2):
        household = Household(model)
        household.setup()
        founder = country.add_citizen(household)
        share = {"founder":founder, "amount":50}
        shares.append(share)
        founders.append(founder)
        founder.account.stocks["cash"] = 50
    country.create_bank(bank, shares)
    return country, bank, founders


@pytest.fixture
def country_with_firm_and_founders(country_with_bank_and_founders, firm, model):
    # Given
    country, _ , founders = country_with_bank_and_founders
    founders = []
    shares = []
    for _ in range(2):
        household = Household(model)
        household.setup()
        founder = country.add_citizen(household)
        share = {"founder":founder, "amount":50}
        shares.append(share)
        founders.append(founder)
        founder.account.stocks["cash"] = 50
    country.create_firm(firm, shares, tradable=True)
    return country, firm, founders



def test_firm_exit_with_residual_cash(country_with_firm_and_founders):
    # Given
    _, firm, founders = country_with_firm_and_founders
    firm.wage_offer = 100

    # When
    firm.exit()

    # Then
    assert firm.account.stocks["cash"] == 0
    assert firm.account.stocks["equities"] == 0
    assert founders[0].account.stocks["cash"] == 50
    assert founders[0].account.stocks["equities"] == 0
    assert founders[1].account.stocks["cash"] == 50
    assert founders[1].account.stocks["equities"] == 0
