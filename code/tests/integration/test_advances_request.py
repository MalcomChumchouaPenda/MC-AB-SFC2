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
def cb(fake_model, union):
    # Given
    cb = CentralBank(fake_model)
    country = union.spaces["country_0"]
    country.add_monetary_authority(cb)
    return cb


@pytest.fixture
def bank(fake_model, union, cb):
    # Given
    bank = Bank(fake_model)
    bank.cb_id = cb.id
    country = union.spaces["country_0"]
    country.add_company(bank, "B")
    market = union.spaces["credit_market"]
    market.add_lender(bank)
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
