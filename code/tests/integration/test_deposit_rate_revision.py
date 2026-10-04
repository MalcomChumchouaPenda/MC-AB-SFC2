from unittest.mock import Mock
import pytest
from model.agents.bank import Bank
from model.spaces.country import Country


@pytest.fixture
def country(fake_model):
    # Given
    model = fake_model
    country = Country(model)
    country.create_markets()
    country.monetary_authority = Mock()
    return country


@pytest.fixture
def bank(fake_model, country):
    # Given
    bank = Bank(fake_model)
    country.place_bank(bank)
    return bank


def test_sets_bank_deposit_rate(bank, country):
    # Given
    bank.p.zeta = 0.8
    country.monetary_authority.discount_rate = 0.04

    # When
    bank.update_deposit_rate()

    # Then
    assert bank.deposit_rate == 0.032
