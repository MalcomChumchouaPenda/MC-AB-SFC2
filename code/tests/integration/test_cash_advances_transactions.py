import math
import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent, CentralBankAgent, GovernmentAgent
from mc_ab_sfc.spaces import CountrySpace


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.mu2 = 0.10
    return model


@pytest.fixture
def govt(model):
    return GovernmentAgent(model)


@pytest.fixture
def central_bank(model):
    # Given
    central_bank = CentralBankAgent(model)
    central_bank.reserves = 50
    central_bank.discount_rate = 0.05
    return central_bank


@pytest.fixture
def country(model, govt, central_bank):
    # Given
    return CountrySpace(model, govt, central_bank)


@pytest.fixture
def bank(model):
    # Given
    bank = BankAgent(model)
    bank.deposits = 1000
    bank.reserves = 50
    return bank


def test_bank_requests_cash_advance(bank, central_bank, country):
    # Given
    country.add_commercial_bank(bank)

    # When
    bank.request_cash_advances()

    # Then
    assert bank.reserves == 100
    assert bank.cash_advances == 50
    assert central_bank.reserves == 100
    assert central_bank.cash_advances == 50
