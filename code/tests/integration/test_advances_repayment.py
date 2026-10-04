import pytest
from model.agents.bank import Bank
from model.agents.central_bank import CentralBank
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def union(fake_model):
    # Given
    union = MonetaryUnion(fake_model)
    union.create_markets()
    union.create_countries(1)
    return union


@pytest.fixture
def country(union):
    # Given
    country = union.spaces["country_0"]
    return country


@pytest.fixture
def cb(fake_model, union):
    # Given
    cb = CentralBank(fake_model)
    cb.national = True
    union.place_central_bank(cb)
    return cb


@pytest.fixture
def bank(fake_model, union):
    # Given
    bank = Bank(fake_model)
    union.place_bank(bank)
    return bank


def test_decreases_advances(bank, cb, country):
    # Given
    bank.account["advances"] = -100
    cb.account["advances"] = 100
    country.discount_rate = 0.05

    # When
    bank.repay_cash_advances()

    # Then
    assert bank.account["advances"] == 0
    assert cb.account["advances"] == 0


def test_increases_advance_interests(bank, cb, country):
    # Given
    bank.account["advances"] = -100
    cb.account["advances"] = 100
    country.discount_rate = 0.05

    # When
    bank.repay_cash_advances()

    # Then
    assert bank.account["adv_interests"] == -5
    assert cb.account["adv_interests"] == 5


def test_transfers_cash(bank, cb, country):
    # Given
    bank.account["advances"] = -100
    cb.account["advances"] = 100
    country.discount_rate = 0.05

    # When
    bank.repay_cash_advances()

    # Then
    assert bank.account["cash"] == -105
    assert cb.account["cash"] == 105
