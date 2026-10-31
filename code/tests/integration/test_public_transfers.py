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
    model.p.household_number = 0
    model.p.initial_public_transfer = 0.0
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
    govt.country_pos = country.pos
    country.add_agents([govt])
    return govt


@pytest.fixture
def cb(model, country):
    # Given
    cb = CentralBank(model)
    cb.national = True
    cb.country_pos = country.pos
    country.add_central_bank(cb)
    return cb


def test_central_bank_transfer_profits(govt, cb, country):
    # Given
    cb.account["adv_interests"] = 50
    cb.account["bond_interests"] = 100
    cash = country.cash
    cash[govt.id].interests = 20

    # When
    cb.transfer_profit()

    # Then
    assert cb.account["profit_transfers"] == -130
    assert govt.account["profit_transfers"] == 130
    assert cash[govt.id].amount == 130


@pytest.fixture
def households(model, country):
    # Given
    households = []
    for _ in range(4):
        household = Household(model)
        household.country_pos = country.pos
        households.append(household)
        country.add_agents([household])
    return households


def test_government_pay_public_transfer_equally(govt, households, country):
    # Given
    govt.public_spending = 400
    cash = country.cash

    # When
    govt.pay_public_transfers()

    # Then
    assert cash[govt.id].amount == -400
    assert govt.account["public_transfers"] == -400
    for household in households:
        assert cash[household.id].amount == 100
        assert household.account["public_transfers"] == 100
