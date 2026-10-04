from unittest.mock import Mock
import pytest
from model.spaces.monetary_union import MonetaryUnion
from model.agents.household import Household
from model.agents.firm import Firm


@pytest.fixture
def model(fake_model, make_dlist):
    # Given
    model = fake_model
    model.firms = make_dlist()
    return model


@pytest.fixture
def union(fake_model):
    # Given
    union = MonetaryUnion(fake_model)
    union.create_markets()
    union.create_countries(1)
    country = union.spaces["country_0"]
    country.monetary_authority = Mock()
    return union


@pytest.fixture
def founders(model, union):
    # Given
    founders = []
    for _ in range(2):
        household = Household(model)
        union.place_household(household)
        founders.append(household)
    return founders


@pytest.fixture
def firm(model, union, founders):
    # Given
    firm = Firm(model)
    union.place_firm(firm)
    for household in founders:
        household.account["cash"] = 50
        citizen = household.roles["citizen"]
        citizen.fund_company(firm.id, 50)
    return firm


def test_firm_exit_with_residual_cash(firm, founders):
    # Given
    firm.wage_offer = 100

    # When
    firm.exit()

    # Then
    assert firm.account["cash"] == 0
    assert firm.account["equities"] == 0
    for founder in founders:
        assert founder.account["cash"] == 50
        assert founder.account["equities"] == 0
