import math
import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent, CentralBankAgent
from mc_ab_sfc.spaces import MonetaryUnionSpace


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.mu2 = 0.10
    return model


@pytest.fixture
def central_bank(model):
    # Given
    central_bank = CentralBankAgent(model)
    central_bank.reserves = 50
    central_bank.discount_rate = 0.05
    return central_bank


@pytest.fixture
def union(model, central_bank):
    # Given
    return MonetaryUnionSpace(model, central_bank)


@pytest.fixture
def bank(model):
    # Given
    bank = BankAgent(model)
    bank.deposits = 1000
    bank.reserves = 50
    return bank


def test_bank_requests_cash_advance(bank, central_bank, union):
    # Given
    union.add_commercial_bank(bank)

    # When
    bank.request_cash_advances()

    # Then
    assert bank.reserves == 100
    assert bank.cash_advances == 50
    assert central_bank.reserves == 100
    assert central_bank.cash_advances == 50
