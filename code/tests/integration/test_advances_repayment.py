import pytest
from model.agents.bank import Bank
from model.agents.central_bank import CentralBank
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def country_with_market(fake_model):
    # Given
    model = fake_model
    model.p.K = 1
    union = MonetaryUnion(model)
    union.build_space()
    country = union.spaces["country_0"]
    market = union.spaces["credit_market"]
    return country, market


@pytest.fixture
def cb(fake_model, country_with_market):
    # Given
    model = fake_model
    cb = CentralBank(model)
    country, _ = country_with_market
    country.add_monetary_authority(cb)
    return cb


@pytest.fixture
def bank(fake_model, country_with_market, cb):
    # Given
    model = fake_model
    bank = Bank(model)
    bank.cb_id = cb.id
    country, market = country_with_market
    country.add_company(bank, "B")
    market.add_lender(bank)
    return bank


def test_decreases_advances(bank, cb):
    # Given
    bank.account["advances"] = -100
    cb.account["advances"] = 100
    cb.roles["monetary_authority"].discount_rate = 0.05

    # When
    bank.repay_cash_advances()

    # Then
    assert bank.account["advances"] == 0
    assert cb.account["advances"] == 0


def test_increases_advance_interests(bank, cb):
    # Given
    bank.account["advances"] = -100
    cb.account["advances"] = 100
    cb.roles["monetary_authority"].discount_rate = 0.05

    # When
    bank.repay_cash_advances()

    # Then
    assert bank.account["adv_interests"] == -5
    assert cb.account["adv_interests"] == 5


def test_transfers_cash(bank, cb):
    # Given
    bank.account["advances"] = -100
    cb.account["advances"] = 100
    cb.roles["monetary_authority"].discount_rate = 0.05

    # When
    bank.repay_cash_advances()

    # Then
    assert bank.account["cash"] == -105
    assert cb.account["cash"] == 105
