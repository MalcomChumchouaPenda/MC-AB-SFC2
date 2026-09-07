import pytest
from unittest.mock import Mock, PropertyMock
from model.spaces.country import Country
from model.agents.government import Government
from model.agents.central_bank import CentralBank
from model.agents.household import Household


@pytest.fixture
def model():
    # Given
    model = Mock()
    return model


@pytest.fixture
def govt(model):
    # Given
    govt = Government(model)
    govt.setup()
    govt.country = "any"
    return govt


@pytest.fixture
def cb(model, monkeypatch):
    # Given
    bond_interests = PropertyMock(return_value=100)
    monkeypatch.setattr(CentralBank, "bond_interests", bond_interests)
    cb = CentralBank(model)
    cb.setup()
    cb.cash_advance_interest = 50
    cb.reserve_interest = 20
    return cb


def test_central_bank_transfer_profits(govt, cb):
    # Given
    cb.government = govt

    # When
    cb.transfer_profit()

    # Then
    assert cb.profits == 130
    assert cb.reserves == 130
    assert govt.profits == 130
    assert govt.reserves == 130


@pytest.fixture
def households(model):
    # Given
    households = []
    for _ in range(4):
        household = Household(model)
        household.country = "any"
        households.append(household)
    model.households = households
    return households


def test_government_pay_public_transfer_equally(govt, households):
    # Given
    govt.reserves = 1000
    govt.public_spending = 400

    # When
    govt.pay_public_transfers()

    # Then
    assert govt.reserves == 600
    assert govt.public_transfers == 400
    for household in households:
        assert household.cash == 100
        assert household.public_transfers == 100
