import pytest
from model.agents.firm import Firm
from model.agents.household import Household
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.initial_wage = 0.0
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.create_markets()
    union.create_countries(1)
    return union


@pytest.fixture
def markets(union, make_dlist):
    # Given
    country = union.spaces["country_0"]
    trad_market = union.spaces["goods_market"]
    non_trad_market = country.spaces["goods_market"]
    return make_dlist([trad_market, non_trad_market])


@pytest.fixture
def household(model, union):
    # Given
    model.p.psi = 2
    model.p.beta = 1
    model.p.cT = 0.6
    household = Household(model)
    union.add_household(household)
    return household


@pytest.fixture
def firms(model, union, make_dlist):
    # Given
    firms = make_dlist()
    for tradable in [True, False]:
        firm = Firm(model)
        firm.tradable = tradable
        firm.variety = 0.5
        firms.append(firm)
        union.add_firm(firm)
    return firms


def test_increases_consumption_of_all_goods(household, firms, markets):
    # Given
    markets.average_price = 10
    household.desired_consumption = 100
    household.account["cash"] = 100
    for firm in firms:
        firm.roles["producer"].inventories = 10
        firm.roles["producer"].price = 10

    # When
    household.consume()

    # Then
    assert household.account["consumption"] == -100
    assert firms[0].account["consumption"] == 60
    assert firms[1].account["consumption"] == 40


def test_transfers_cash_for_all_consumptions(household, firms, markets):
    # Given
    markets.average_price = 10
    household.desired_consumption = 100
    household.account["cash"] = 100
    for firm in firms:
        firm.roles["producer"].inventories = 10
        firm.roles["producer"].price = 10

    # When
    household.consume()

    # Then
    assert household.account["cash"] == 0
    assert firms[0].account["cash"] == 60
    assert firms[1].account["cash"] == 40


def test_reduces_inventories_of_firms(household, firms, markets):
    # Given
    markets.average_price = 10
    household.desired_consumption = 100
    household.account["cash"] = 100
    for firm in firms:
        firm.roles["producer"].inventories = 10
        firm.roles["producer"].price = 10

    # When
    household.consume()

    # Then
    assert firms[0].roles["producer"].inventories == 4
    assert firms[1].roles["producer"].inventories == 6
