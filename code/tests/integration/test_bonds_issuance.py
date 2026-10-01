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
    union.build_space()
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
    union.spaces["bond_market"].add_issuer(govt)
    return govt, country


def test_sets_govt_debt_ratio(govt_with_country):
    # Given
    govt, country = govt_with_country
    govt.prev_budget_surplus = 50
    govt.budget_deficit = 200
    country.gdp = 1000

    # When
    govt.issue_bonds()

    # Then
    assert govt.roles["bond_issuer"].debt_ratio == 0.15


def test_sets_govt_bonds_number_and_value(govt_with_country):
    # Given
    govt, country = govt_with_country
    govt.prev_budget_surplus = 50
    govt.budget_deficit = 200
    country.gdp = 1000

    # When
    govt.issue_bonds()

    # Then
    assert govt.roles["bond_issuer"].bond_value == 1.5
    assert govt.roles["bond_issuer"].bond_number == 100
