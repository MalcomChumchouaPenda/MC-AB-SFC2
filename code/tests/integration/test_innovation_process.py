from unittest.mock import Mock
import pytest
from model.agents.firm import Firm
from model.spaces.goods_market import GoodsMarket


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.delta = 0.2
    model.p.gamma = 0.1
    model.p.nu = 1
    return model


@pytest.fixture
def market(model):
    # Given
    market = GoodsMarket(model)
    return market


@pytest.fixture
def firm(model, market):
    # Given
    firm = Firm(model)
    market.place_firm(firm)
    return firm


@pytest.fixture
def random(monkeypatch, model):
    # Given
    random = Mock()
    random.choice.return_value = 1
    monkeypatch.setattr(model, "nprandom", random)
    return random


@pytest.fixture
def before_innovation(firm):
    # Given
    firm.wage_offer = 10
    firm.desired_labor = 100
    firm.labor = 100
    firm.desired_rd = 100
    firm.desired_loans = 100
    firm.account["loans"] = 100


@pytest.mark.usefixtures("before_innovation")
def test_increases_productivity_with_success(firm, market, random):
    # Given
    firm.roles["producer"].productivity = 10
    market.average_prod = 10
    market.average_price = 10
    random.uniform.return_value = 0.2

    # When
    firm.update_productivity()

    # Then
    assert firm.roles["producer"].productivity == 12


@pytest.mark.usefixtures("before_innovation")
def test_dont_increases_productivity_without_success(firm, market, random):
    # Given
    firm.roles["producer"].productivity = 10
    market.average_prod = 10
    market.average_price = 10
    random.choice.return_value = 0

    # When
    firm.update_productivity()

    # Then
    assert firm.roles["producer"].productivity == 10


@pytest.mark.usefixtures("before_innovation")
def test_increases_prductivity_by_imitation(firm, market, random):
    # Given
    firm.roles["producer"].productivity = 10
    market.average_prod = 15
    market.average_price = 10
    random.uniform = lambda a, b: b

    # When
    firm.update_productivity()

    # Then
    assert firm.roles["producer"].productivity == 15
