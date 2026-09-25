from unittest.mock import Mock
import pytest
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
    union.monetary_authority = Mock()
    union.spaces["country_0"].monetary_authority = Mock()
    return union


@pytest.fixture
def firm(model):
    # Given
    return Firm(model)


@pytest.fixture
def bank(model):
    # Given
    return Bank(model)


@pytest.fixture
def households(model):
    # Given
    return [Household(model) for _ in range(2)]


@pytest.fixture
def country_with_firm_and_founders(union, firm, households):
    # Given
    country = union.spaces["country_0"]
    founders = []
    shares = []
    for household in households:
        founder = country.add_citizen(household)
        share = {"founder": founder, "amount": 50}
        shares.append(share)
        founders.append(founder)
        household.account.stocks["cash"] = 50
    country.create_firm(firm, shares, tradable=True)
    return country, firm, founders


def test_firm_exit_with_residual_cash(country_with_firm_and_founders):
    # Given
    country, firm, founders = country_with_firm_and_founders
    firm.wage_offer = 100

    # When
    firm.exit()

    # Then
    assert firm.account.stocks["cash"] == 0
    assert firm.account.stocks["equities"] == 0
    for founder in founders:
        assert country.get_stock("cash", founder.id) == 50
        assert country.get_stock("equities", founder.id) == 0
