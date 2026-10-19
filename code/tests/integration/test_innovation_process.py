from unittest.mock import Mock
import pytest
from model.agents.firm import Firm
from model.spaces.country import Country


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.delta = 0.2
    model.p.gamma = 0.1
    model.p.nu = 1
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.create_markets()
    market = country.spaces["goods_market"]
    market.average_prod = 10
    market.average_price = 10
    return country


@pytest.fixture
def firm(model, country):
    # Given
    firm = Firm(model)
    firm.desired_rd = 100
    firm.desired_labor = 100
    firm.desired_loans = 100
    country.add_agents([firm])
    firm.account["loans"] = 100
    firm.roles["employer"].labor = 100
    firm.roles["employer"].wage = 10
    return firm


@pytest.fixture
def random(monkeypatch, model):
    # Given
    random = Mock()
    random.choice.return_value = 1
    monkeypatch.setattr(model, "nprandom", random)
    return random


def test_increases_productivity_with_success(firm, random):
    # Given
    firm.roles["producer"].productivity = 10
    random.uniform.return_value = 0.2

    # When
    firm.execute_rd()

    # Then
    assert firm.roles["producer"].productivity == 12


def test_dont_increases_productivity_without_success(firm, random):
    # Given
    firm.roles["producer"].productivity = 10
    random.choice.return_value = 0

    # When
    firm.execute_rd()

    # Then
    assert firm.roles["producer"].productivity == 10


def test_increases_prductivity_by_imitation(firm, country, random):
    # Given
    firm.roles["producer"].productivity = 10
    country.spaces["goods_market"].average_prod = 15
    random.uniform = lambda a, b: b

    # When
    firm.execute_rd()

    # Then
    assert firm.roles["producer"].productivity == 15
