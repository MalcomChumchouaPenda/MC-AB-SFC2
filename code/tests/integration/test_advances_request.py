import pytest
from model.agents.bank import Bank
from model.agents.central_bank import CentralBank
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.create_markets()
    union.create_countries(1)
    return union


@pytest.fixture
def cb(model, union):
    # Given
    cb = CentralBank(model)
    cb.national = True
    union.add_central_bank(cb)
    return cb


@pytest.fixture
def bank(model, union):
    # Given
    bank = Bank(model)
    union.add_bank(bank)
    return bank


def test_increases_advances(bank, cb):
    # Given
    bank.p.mu2 = 0.10
    bank.account["cash"] = 40
    bank.account["deposits"] = 1000

    # When
    bank.request_cash_advances()

    # Then
    assert bank.account["advances"] == -60
    assert cb.account["advances"] == 60


def test_transfers_cash(bank, cb):
    # Given
    bank.p.mu2 = 0.10
    bank.account["cash"] = 40
    bank.account["deposits"] = 1000

    # When
    bank.request_cash_advances()

    # Then
    assert bank.account["cash"] == 100
    assert cb.account["cash"] == -60
