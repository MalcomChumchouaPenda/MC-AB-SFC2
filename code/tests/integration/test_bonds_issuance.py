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
    return country


@pytest.fixture
def govt(fake_model, union):
    # Given
    govt = Government(fake_model)
    union.place_government(govt)
    return govt


def test_sets_govt_debt_ratio(govt, country):
    # Given
    govt.prev_budget_surplus = 50
    govt.budget_deficit = 200
    country.gdp = 1000

    # When
    govt.issue_bonds()

    # Then
    assert govt.roles["bond_issuer"].debt_ratio == 0.15


def test_sets_govt_bonds_number_and_value(govt, country):
    # Given
    govt.prev_budget_surplus = 50
    govt.budget_deficit = 200
    country.gdp = 1000

    # When
    govt.issue_bonds()

    # Then
    assert govt.roles["bond_issuer"].bond_value == 1.5
    assert govt.roles["bond_issuer"].bond_number == 100
