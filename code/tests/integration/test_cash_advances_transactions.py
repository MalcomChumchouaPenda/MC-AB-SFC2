import math
import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent, CentralBankAgent
from mc_ab_sfc.spaces import BankSystem


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.mu2 = 0.10
    return model


@pytest.fixture
def bank_system(model):
    # Given
    return BankSystem(model)


@pytest.fixture
def central_bank(model, bank_system):
    # Given
    agent = CentralBankAgent(model)
    bank_system.add_central_bank(agent)
    return agent


@pytest.fixture
def bank(model, central_bank, bank_system):
    # Given
    bank = BankAgent(model)
    central_role = central_bank.roles["central_bank"]
    bank_role = bank_system.add_commercial_bank(bank)
    bank_system.assign_central_bank(bank_role, central_role)
    return bank


def test_bank_requests_cash_advance(bank, central_bank):
    # Given
    central_bank.reserves = 50
    central_bank.discount_rate = 0.05
    bank.deposits = 1000
    bank.reserves = 50

    # When
    bank.request_cash_advances()

    # Then
    assert bank.reserves == 100
    assert bank.cash_advances == 50
    assert central_bank.reserves == 100
    assert central_bank.cash_advances == 50
