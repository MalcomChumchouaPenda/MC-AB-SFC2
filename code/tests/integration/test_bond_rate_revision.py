from unittest.mock import Mock
import pytest
from model.agents.government import Government
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def union(fake_model):
    # Given
    model = fake_model
    model.p.K = 1
    union = MonetaryUnion(model)
    return union


@pytest.fixture
def govt(fake_model):
    # Given
    model = fake_model
    govt = Government(model)
    return govt


@pytest.fixture
def govt_with_country(govt, union):
    # Given
    country = union.spaces["country_0"]
    country.monetary_authority = Mock()
    country.add_fiscal_authority(govt)
    return govt, country


def test_sets_govt_bond_rate(govt_with_country):
    # Given
    govt, country = govt_with_country
    govt.account["bonds"] = 100
    govt.p.chi = 0.02
    country.gdp = 1000
    country.monetary_authority.discount_rate = 0.04

    # When
    govt.update_bond_rate()

    # Then
    assert govt.bond_rate == 0.042
