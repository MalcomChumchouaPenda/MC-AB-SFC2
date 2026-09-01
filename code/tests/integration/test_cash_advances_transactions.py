import math
import pytest
from unittest.mock import Mock, PropertyMock
from model.agents.bank import Bank
from model.agents.central_bank import NationalCentralBank
from model.spaces.country import Country


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.mu2 = 0.10
    return model


@pytest.fixture
def cb(model):
    # Given
    union_cb = Mock(discount_rate=0.05)
    cb = NationalCentralBank(model)
    cb.setup()
    cb.reserves = 50
    cb.union_bank = union_cb
    return cb


@pytest.fixture
def bank(model, monkeypatch):
    # Given
    mock_deposits = PropertyMock(return_value=1000)
    monkeypatch.setattr(Bank, "deposits", mock_deposits)
    bank = Bank(model)
    bank.reserves = 50
    return bank


def test_bank_requests_cash_advance(bank, cb):
    # Given
    bank.central_bank = cb

    # When
    bank.request_cash_advances()

    # Then
    assert bank.reserves == 100
    assert bank.cash_advances == 50
    assert cb.reserves == 100
    assert cb.cash_advances == 50
