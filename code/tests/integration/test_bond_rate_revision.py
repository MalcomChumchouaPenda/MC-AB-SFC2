from unittest.mock import Mock
import pytest
from model.agents.government import Government
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def union(fake_model):
    # Given
    union = MonetaryUnion(fake_model)
    union.create_markets()
    union.create_countries(1)
    return union


@pytest.fixture
def country(union):
    # Given
    country = union.spaces["country_0"]
    country.monetary_authority = Mock()
    return country


@pytest.fixture
def govt(fake_model, country):
    # Given
    govt = Government(fake_model)
    country.add_fiscal_authority(govt)
    return govt


def test_sets_govt_bond_rate(govt, country):
    # Given
    govt.account["bonds"] = 100
    govt.p.chi = 0.02
    country.gdp = 1000
    country.monetary_authority.discount_rate = 0.04

    # When
    govt.update_bond_rate()

    # Then
    assert govt.bond_rate == 0.042
