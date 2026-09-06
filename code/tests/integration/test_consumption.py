import pytest
from unittest.mock import Mock
from agentpy import Model
from model.base import EcoAccount
from model.agents.firm import Firm
from model.agents.household import Household
from model.spaces.good_market import GoodsMarket


@pytest.fixture
def model():
    # Given
    model = Model()
    model.p.psi = 2
    model.p.beta = 1
    return model


@pytest.fixture
def household(model):
    # Given
    household = Household(model)
    household.setup()
    household.account = EcoAccount(model)
    household.account.setup()
    household.account.stocks["cash"] = 100
    return household


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.setup()
    firm.account = EcoAccount(model)
    firm.account.setup()
    return firm


@pytest.fixture
def trad_market(model, household, firm):
    # Given
    market = GoodsMarket(model)
    market.setup()
    market.tradable = True
    market.add_consumer(household)
    market.add_producer(firm)
    return market


def test_household_consume_tradable_goods(trad_market, household, firm):
    # Given
    household.account.stocks["cash"] = 100
    consumer_role = household.roles["trad_consumer"]
    producer_role = firm.roles["producer"]
    producer_role.price = 10
    producer_role.inventories = 10
    trad_market.average_price = 10
    firm.variety = 0.5

    # When
    household.consume_good(consumer_role, 60)

    # Then
    assert household.account.stocks["cash"] == 40
    assert household.account.flows["consumption"] == -60
    assert firm.account.stocks["cash"] == 60
    assert firm.account.flows["consumption"] == 60
    assert producer_role.inventories == 4


@pytest.fixture
def non_trad_market(model, household, firm):
    # Given
    market = GoodsMarket(model)
    market.setup()
    market.tradable = False
    market.add_consumer(household)
    market.add_producer(firm)
    return market


def test_household_consume_non_trad_goods(non_trad_market, household, firm):
    # Given
    household.account.stocks["cash"] = 100
    consumer_role = household.roles["non_trad_consumer"]
    producer_role = firm.roles["producer"]
    producer_role.price = 10
    producer_role.inventories = 10
    non_trad_market.average_price = 10
    firm.variety = 0.5

    # When
    household.consume_good(consumer_role, 40)

    # Then
    assert household.account.stocks["cash"] == 60
    assert household.account.flows["consumption"] == -40
    assert firm.account.stocks["cash"] == 40
    assert firm.account.flows["consumption"] == 40
    assert producer_role.inventories == 6


@pytest.fixture
def firms(model):
    # Given
    firms = []
    for _ in range(2):
        firm = Firm(model)
        firm.setup()
        firm.variety = 0.5
        firm.account = EcoAccount(model)
        firm.account.setup()
        firms.append(firm)
    return firms


@pytest.fixture
def markets_with_inventories(model, household, firms):
    markets = []
    for i, tradable in enumerate([True, False]):
        market = GoodsMarket(model)
        market.setup()
        market.tradable = tradable
        market.average_price = 10
        market.add_consumer(household)
        markets.append(market)
        producer_role = market.add_producer(firms[i])
        producer_role.price = 10
        producer_role.inventories = 10
    return markets


@pytest.mark.usefixtures("markets_with_inventories")
def test_household_consumes_all_goods(household, firms):
    # Given
    household.p.cT = 0.6
    household.desired_consumption = 100
    household.account.stocks["cash"] = 100

    # When
    household.consume()

    # Then
    assert firms[0].account.flows["consumption"] == 60
    assert firms[1].account.flows["consumption"] == 40
