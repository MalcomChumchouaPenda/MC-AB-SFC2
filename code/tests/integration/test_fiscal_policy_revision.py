from unittest.mock import Mock
import pytest
from model.spaces.country import Country
from model.agents.government import Government


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.dmax = 0.05
    model.p.tax_min = 0.10
    model.p.tax_max = 0.50
    model.p.g_min = 0.05
    model.p.g_max = 0.20
    model.p.delta = 0.10
    return model


@pytest.fixture
def country(fake_model):
    # Given
    country = Country(fake_model)
    country.create_markets()
    country.spaces["goods_market"].average_price = 2
    country.spaces["goods_market"].average_prod = 3
    country.gdp = 1000
    return country


@pytest.fixture
def govt(model, country):
    # Given
    govt = Government(model)
    govt.prev_public_spending = 10
    govt.public_spending = 100
    govt.budget_deficit = 100
    govt.next_tax_rate = 0.20
    country.add_government(govt)
    return govt


@pytest.fixture
def random(monkeypatch, model):
    # Given
    random = Mock()
    monkeypatch.setattr(model, "random", random)
    return random


def test_updates_desired_public_spending(govt, random):
    # Given
    random.uniform.return_value = 0.05

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.desired_public_spending == pytest.approx(60)


def test_updates_public_spending(govt, random):
    # Given
    random.uniform.return_value = 0.05

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(95)


def test_updates_next_tax_rate(govt, random):
    # Given
    random.uniform.return_value = 0.05

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.next_tax_rate == pytest.approx(0.21)
