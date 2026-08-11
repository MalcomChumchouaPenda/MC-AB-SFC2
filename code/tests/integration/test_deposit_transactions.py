import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent, FirmAgent
from mc_ab_sfc.spaces import DepositMarket, CountrySpace


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.zeta = 0.8
    return model


@pytest.fixture
def bank(model):
    # Given
    bank = BankAgent(model)
    bank.deposits = 2000
    return bank


@pytest.fixture
def firm(model):
    # Given
    firm = FirmAgent(model)
    firm.deposits = 1000
    return firm


@pytest.fixture
def country(model):
    # Given
    country = CountrySpace(model)
    country.discount_rate = 0.05
    return country


@pytest.fixture
def deposit_market(model):
    # Given
    return DepositMarket(model)


def test_bank_pays_deposit_interest(firm, bank, country, deposit_market):
    # Given
    bank_role = deposit_market.add_deposit_bank(bank)
    firm_role = deposit_market.add_deposit_holder(firm)
    deposit_market.assign_deposit_bank(firm_role, bank_role)
    country.central_bank_role = Mock()
    country.add_commercial_bank(bank)

    # When
    bank.update_deposit_rate()
    bank.pay_deposit_interest()

    # Then
    assert firm.deposits == pytest.approx(1040)
    assert bank.deposits == pytest.approx(2040)
    assert firm.deposit_interest == pytest.approx(40)
    assert bank.deposit_interest == pytest.approx(40)
