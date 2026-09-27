from unittest.mock import Mock
import pytest
from model.agents.bank import Bank
from model.agents.central_bank import CentralBank
from model.spaces.credit_market import CreditMarket


@pytest.fixture
def cb(fake_model):
    # Given
    model = fake_model
    return CentralBank(model)


@pytest.fixture
def bank(fake_model, cb):
    # Given
    model = fake_model
    bank = Bank(model)
    bank.cb_id = cb.id
    bank.roles["company"] = Mock()
    return bank


@pytest.fixture
def market_participants(fake_model, bank, cb):
    # Given
    model = fake_model
    market = CreditMarket(model)
    market.add_lender(bank)
    market.add_account(cb)
    return bank, cb


def test_decreases_advances(market_participants):
    # Given
    bank, cb = market_participants
    bank.roles["company"].get_discount_rate.return_value = 0.05
    bank.account.stocks["advances"] = -100
    cb.account.stocks["advances"] = 100

    # When
    bank.repay_cash_advances()

    # Then
    assert bank.account.stocks["advances"] == 0
    assert cb.account.stocks["advances"] == 0


def test_increases_advance_interests(market_participants):
    # Given
    bank, cb = market_participants
    bank.roles["company"].get_discount_rate.return_value = 0.05
    bank.account.stocks["advances"] = -100
    cb.account.stocks["advances"] = 100

    # When
    bank.repay_cash_advances()

    # Then
    assert bank.account.flows["adv_interests"] == -5
    assert cb.account.flows["adv_interests"] == 5


def test_transfers_cash(market_participants):
    # Given
    bank, cb = market_participants
    bank.roles["company"].get_discount_rate.return_value = 0.05
    bank.account.stocks["advances"] = -100

    # When
    bank.repay_cash_advances()

    # Then
    assert bank.account.stocks["cash"] == -105
    assert cb.account.stocks["cash"] == 105
