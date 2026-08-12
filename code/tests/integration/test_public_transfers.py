import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import CountrySpace
from mc_ab_sfc.agents import GovernmentAgent, CentralBankAgent, HouseholdAgent


@pytest.fixture
def model():
    # Given
    model = Mock()
    return model


@pytest.fixture
def govt(model):
    # Given
    return GovernmentAgent(model)


@pytest.fixture
def central_bank(model):
    # Given
    central_bank = CentralBankAgent(model)
    central_bank.bond_interest = 100
    central_bank.cash_advance_interest = 50
    central_bank.reserve_interest = 20
    return central_bank


@pytest.fixture
def country(model):
    # Given
    return CountrySpace(model)


def test_central_bank_transfer_profits(govt, central_bank, country):
    # Given
    country.add_government(govt)
    country.add_central_bank(central_bank)

    # When
    central_bank.pay_profit()

    # Then
    assert central_bank.profit == 130
    assert central_bank.reserves == 130
    assert govt.profit == 130
    assert govt.reserves == 130


@pytest.fixture
def households(model):
    # Given
    return [HouseholdAgent(model) for _ in range(4)]


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
