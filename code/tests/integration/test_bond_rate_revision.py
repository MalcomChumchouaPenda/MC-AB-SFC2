from unittest.mock import Mock
import pytest
from model.agents.government import Government
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def country(fake_model):
    # Given
    union = MonetaryUnion(fake_model)
    union.create_markets()
    union.create_countries(1)
    return union.spaces["country_0"]


@pytest.fixture
def govt(fake_model, country):
    # Given
    govt = Government(fake_model)
    country.place_government(govt)
    return govt


def test_sets_govt_bond_rate(govt, country):
    # Given
    country.discount_rate = 0.04
    country.gdp = 1000
    govt.p.chi = 0.02
    govt.account["bonds"] = 100

    # When
    govt.update_bond_rate()

    # Then
    assert govt.bond_rate == 0.042
