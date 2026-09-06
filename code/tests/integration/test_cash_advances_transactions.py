import math
import pytest
from unittest.mock import Mock
from model.base import EcoAccount
from model.agents.bank import Bank
from model.spaces.credit_market import CreditMarket


@pytest.fixture
def model():
    # Given
    return Mock()


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    bank.setup()
    bank.account = EcoAccount(model)
    bank.account.setup()
    bank.cb_account = EcoAccount(model)
    bank.cb_account.setup()
    return bank


@pytest.fixture
def market(model, bank):
    # Given
    market = CreditMarket(model)
    market.setup()
    market.add_lender(bank)
    return market


@pytest.mark.usefixtures("market")
def test_bank_requests_cash_advance(bank):
    # Given
    bank.p.mu2 = 0.10
    bank.account.stocks["cash"] = 50
    bank.account.stocks["deposits"] = 1000

    # When
    bank.request_cash_advances()

    # Then
    assert bank.account.stocks["cash"] == 100
    assert bank.account.stocks["advances"] == -50
    assert bank.cb_account.stocks["cash"] == -50
    assert bank.cb_account.stocks["advances"] == 50


@pytest.mark.usefixtures("market")
def test_bank_repays_cash_advance(bank):
    # Given
    bank.account.stocks["advances"] = -100
    bank.roles["company"] = Mock()
    bank.roles["company"].get_discount_rate.return_value = 0.05

    # When
    bank.repay_cash_advances()

    # Then
    assert bank.account.stocks["cash"] == -105
    assert bank.account.stocks["advances"] == 0
    assert bank.account.flows["adv_interests"] == -5
    assert bank.cb_account.stocks["cash"] == 105
    assert bank.cb_account.stocks["advances"] == -100
    assert bank.cb_account.flows["adv_interests"] == 5
