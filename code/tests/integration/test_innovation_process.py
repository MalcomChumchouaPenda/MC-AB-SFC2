import pytest
from unittest.mock import Mock
from model.agents.private import Firm
from model.spaces.real import GoodsMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.gamma = 0.1
    model.p.nu = 1
    model.p.delta = 0.2
    return model


@pytest.fixture
def market(model):
    # Given
    market = GoodsMarket(model)
    market.average_price = 10
    return market


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.productivity = 10
    firm.wage_offer = 10
    firm.desired_labor = 100
    firm.labor = 100
    firm.desired_rd = 100
    firm.desired_loans = 100
    firm.loans = 100
    return firm


def test_firm_innovation_process(firm, market):
    # Given
    producer = market.add_supplier(firm)
    market.average_productivity = 10
    random = market.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.2

    # When
    firm.update_productivity()

    # Then
    assert firm.productivity == 12
    assert producer.productivity == 12


def test_firm_innovation_process(firm, market):
    # Given
    producer = market.add_supplier(firm)
    market.average_productivity = 15
    random = market.model.nprandom
    random.choice.return_value = 1
    random.uniform = lambda a, b: b

    # When
    firm.update_productivity()

    # Then
    assert firm.productivity == 15
    assert producer.productivity == 15
