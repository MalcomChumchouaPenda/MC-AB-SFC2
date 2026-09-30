from unittest.mock import Mock
import pytest
from model.agents.bank import Bank
from model.spaces.country import Country


@pytest.fixture
def country(fake_model):
    # Given
    model = fake_model
    country = Country(model)
    country.monetary_authority = Mock()
    return country


@pytest.fixture
def bank(fake_model, country):
    # Given
    model = fake_model
    bank = Bank(model)
    country.add_company(bank, sector="B")
    market = country.spaces["deposit_market"]
    market.add_deposit_bank(bank)
    return bank


def test_sets_bank_deposit_rate(bank, country):
    # Given
    bank.p.zeta = 0.8
    country.monetary_authority.discount_rate = 0.04

    # When
    bank.update_deposit_rate()

    # Then
    assert bank.deposit_rate == 0.032
