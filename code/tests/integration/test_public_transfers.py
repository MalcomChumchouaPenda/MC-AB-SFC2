from unittest.mock import Mock
import pytest
from model.spaces.country import Country
from model.agents.government import Government
from model.agents.central_bank import CentralBank
from model.agents.household import Household


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.initial_bond_rate = 0.0
    model.p.initial_wage = 0.0
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.create_markets()
    return country


@pytest.fixture
def govt(model, country):
    # Given
    govt = Government(model)
    country.add_government(govt)
    return govt


@pytest.fixture
def cb(model, country):
    # Given
    cb = CentralBank(model)
    cb.national = True
    country.add_central_bank(cb)
    return cb


def test_central_bank_transfer_profits(govt, cb):
    # Given
    cb.account["adv_interests"] = 50
    cb.account["cash_interests"] = 20
    cb.account["bond_interests"] = 100

    # When
    cb.transfer_profit()

    # Then
    assert cb.account["profit_transfers"] == -130
    assert cb.account["cash"] == -130
    assert govt.account["profit_transfers"] == 130
    assert govt.account["cash"] == 130


@pytest.fixture
def households(model, country):
    # Given
    households = []
    for _ in range(4):
        household = Household(model)
        households.append(household)
        country.add_household(household)
    return households


def test_government_pay_public_transfer_equally(govt, households):
    # Given
    govt.public_spending = 400

    # When
    govt.pay_public_transfers()

    # Then
    assert govt.account["cash"] == -400
    assert govt.account["public_transfers"] == -400
    for household in households:
        assert household.account["cash"] == 100
        assert household.account["public_transfers"] == 100
