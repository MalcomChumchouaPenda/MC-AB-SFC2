import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import FirmAgent, BankAgent, GovernmentAgent
from mc_ab_sfc.spaces import CountrySpace


@pytest.fixture
def model():
    # Given
    model = Mock()
    return model


@pytest.fixture
def govt(model):
    # Given
    return GovernmentAgent(model)


@pytest.fixture
def country(model):
    # Given
    return CountrySpace(model)


def test_firm_pay_taxes(model, govt, country):
    # Given
    firm = FirmAgent(model)
    firm.cash = 1000
    firm.taxes_payable = 100
    govt_role = country.add_government(govt)
    payer_role = country.add_tax_payer(firm)
    country.assign_government(payer_role, govt_role)

    # When
    firm.pay_taxes()

    # Then
    assert firm.taxes_payable == 0
    assert firm.taxes == 100
    assert firm.cash == 900
    assert govt.taxes == 100
    assert govt.reserves == 100


def test_bank_pay_taxes(model, govt, country):
    # Given
    bank = BankAgent(model)
    bank.reserves = 1000
    bank.taxes_payable = 100
    govt_role = country.add_government(govt)
    payer_role = country.add_tax_payer(bank)
    country.assign_government(payer_role, govt_role)

    # When
    bank.pay_taxes()

    # Then
    assert bank.taxes_payable == 0
    assert bank.taxes == 100
    assert bank.reserves == 900
    assert govt.taxes == 100
    assert govt.reserves == 100
