import pytest
from unittest.mock import Mock
from model.base import EcoAccount
from model.agents.firm import Firm
from model.spaces.good_market import GoodsMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.gamma = 0.1
    model.p.nu = 1
    model.p.delta = 0.2
    return model


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.setup()
    firm.account = EcoAccount(model)
    firm.account.setup()
    return firm


@pytest.fixture
def market(model, firm):
    # Given
    market = GoodsMarket(model)
    market.setup()
    market.add_producer(firm)
    return market


def test_firm_innovation_process(firm, market):
    # Given
    firm.wage_offer = 10
    firm.desired_labor = 100
    firm.labor = 100
    firm.desired_rd = 100
    firm.desired_loans = 100
    firm.account.stocks["loans"] = 100
    firm.roles["producer"].productivity = 10
    market.average_prod = 10
    market.average_price = 10
    random = market.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.2

    # When
    firm.update_productivity()

    # Then
    assert firm.roles["producer"].productivity == 12


def test_firm_imitation_process(firm, market):
    # Given
    firm.wage_offer = 10
    firm.desired_labor = 100
    firm.labor = 100
    firm.desired_rd = 100
    firm.desired_loans = 100
    firm.account.stocks["loans"] = 100
    firm.roles["producer"].productivity = 10
    market.average_prod = 15
    market.average_price = 10
    random = market.model.nprandom
    random.choice.return_value = 1
    random.uniform = lambda a, b: b

    # When
    firm.update_productivity()

    # Then
    assert firm.roles["producer"].productivity == 15
