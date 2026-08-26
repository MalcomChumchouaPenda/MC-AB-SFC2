import pytest
from unittest.mock import Mock, PropertyMock
from mc_ab_sfc.spaces import CountrySpace
from mc_ab_sfc.agents import Government, CentralBank, Household


@pytest.fixture
def model():
    # Given
    model = Mock()
    return model


@pytest.fixture
def govt(model):
    # Given
    return Government(model)


@pytest.fixture
def cb(model, monkeypatch):
    # Given
    bond_interests = PropertyMock(return_value=100)
    monkeypatch.setattr(CentralBank, "bond_interests", bond_interests)
    cb = CentralBank(model)
    cb.cash_advance_interest = 50
    cb.reserve_interest = 20
    return cb


@pytest.fixture
def country(model):
    # Given
    return CountrySpace(model)


def test_central_bank_transfer_profits(govt, cb, country):
    # Given
    country.add_government(govt)
    country.add_central_bank(cb)

    # When
    cb.pay_profit()

    # Then
    assert cb.profit == 130
    assert cb.reserves == 130
    assert govt.profit == 130
    assert govt.reserves == 130


@pytest.fixture
def households(model):
    # Given
    return [Household(model) for _ in range(4)]


def test_government_pay_public_transfer_equally(govt, households, country):
    # Given
    govt.reserves = 1000
    govt.public_spending = 400
    country.add_government(govt)
    for household in households:
        country.add_tax_payer(household)

    # When
    govt.pay_public_transfers()

    # Then
    assert govt.reserves == 600
    assert govt.public_transfers == 400
    for household in households:
        assert household.cash == 100
        assert household.public_transfers == 100
