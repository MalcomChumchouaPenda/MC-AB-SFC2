from unittest.mock import Mock
import pytest
from agentpy import Model
from model.agents.bank import Bank
from model.agents.central_bank import CentralBank
from model.spaces.credit_market import CreditMarket


@pytest.fixture
def model():
    # Given
    model = Model()
    return model


@pytest.fixture
def bank(model):
    # Given
    return Bank(model)


@pytest.fixture
def cb(model):
    # Given
    return CentralBank(model)


@pytest.fixture
def market(model):
    # Given
    market = CreditMarket(model)
    return market


@pytest.fixture
def before_transactions(market, bank, cb):
    # Given
    bank.cb_id = cb.id
    market.add_lender(bank)
    market.add_account(cb)


@pytest.mark.usefixtures("before_transactions")
def test_bank_requests_cash_advance(bank, cb):
    # Given
    bank.p.mu2 = 0.10
    bank.account.stocks["cash"] = 50
    bank.account.stocks["deposits"] = 1000

    # When
    bank.request_cash_advances()

    # Then
    assert bank.account.stocks["cash"] == 100
    assert bank.account.stocks["advances"] == -50
    assert cb.account.stocks["cash"] == -50
    assert cb.account.stocks["advances"] == 50


@pytest.mark.usefixtures("before_transactions")
def test_bank_repays_cash_advance(bank, cb):
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
    assert cb.account.stocks["cash"] == 105
    assert cb.account.stocks["advances"] == -100
    assert cb.account.flows["adv_interests"] == 5
