import math
import pytest
from unittest.mock import Mock, PropertyMock
from mc_ab_sfc.agents import Bank, CentralBank
from mc_ab_sfc.spaces import CountrySpace


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.mu2 = 0.10
    return model


@pytest.fixture
def central_bank(model):
    # Given
    central_bank = CentralBank(model)
    central_bank.reserves = 50
    central_bank.discount_rate = 0.05
    return central_bank


@pytest.fixture
def bank(model, monkeypatch):
    # Given
    mock_deposits = PropertyMock(return_value=1000)
    monkeypatch.setattr(Bank, "deposits", mock_deposits)
    bank = Bank(model)
    bank.reserves = 50
    return bank


@pytest.fixture
def country(model):
    # Given
    country = CountrySpace(model)
    country.government_role = Mock()
    return country


def test_bank_requests_cash_advance(bank, central_bank, country):
    # Given
    country.add_central_bank(central_bank)
    country.add_commercial_bank(bank)

    # When
    bank.request_cash_advances()

    # Then
    assert bank.reserves == 100
    assert bank.cash_advances == 50
    assert central_bank.reserves == 100
    assert central_bank.cash_advances == 50
