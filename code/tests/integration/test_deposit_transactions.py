import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent, FirmAgent, CentralBankAgent
from mc_ab_sfc.spaces import DepositMarket, MonetaryUnionSpace


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.zeta = 0.8
    return model


@pytest.fixture
def monetary_union(model):
    # Given
    return MonetaryUnionSpace(model)


@pytest.fixture
def deposit_market(model):
    # Given
    return DepositMarket(model)


@pytest.fixture
def central_bank(model, monetary_union):
    # Given
    central_bank = CentralBankAgent(model)
    monetary_union.add_central_bank(central_bank)
    return central_bank


@pytest.fixture
def bank(model, central_bank, monetary_union, deposit_market):
    # Given
    bank = BankAgent(model)
    central_role = central_bank.roles["central_bank"]
    bank_role = monetary_union.add_commercial_bank(bank)
    monetary_union.assign_central_bank(bank_role, central_role)
    deposit_market.add_deposit_bank(bank)
    return bank


@pytest.fixture
def firm(model, bank, deposit_market):
    # Given
    firm = FirmAgent(model)
    bank_role = bank.roles["deposit_bank"]
    firm_role = deposit_market.add_deposit_holder(firm)
    deposit_market.assign_deposit_bank(firm_role, bank_role)
    return firm


def test_bank_pays_deposit_interest(firm, bank, central_bank):
    # Given
    firm.deposits = 1000
    bank.deposits = 2000
    central_bank.discount_rate = 0.05

    # When
    bank.update_deposit_rate()
    bank.pay_deposit_interest()

    # Then
    assert firm.deposits == pytest.approx(1040)
    assert bank.deposits == pytest.approx(2040)
    assert firm.deposit_interest == pytest.approx(40)
    assert bank.deposit_interest == pytest.approx(40)
