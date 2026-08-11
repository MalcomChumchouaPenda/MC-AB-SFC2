import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import CountrySpace
from mc_ab_sfc.agents import FirmAgent, BankAgent, GovernmentAgent, CentralBankAgent


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.rho = 0.10
    return model


@pytest.fixture
def govt(model):
    # Given
    govt = GovernmentAgent(model)
    govt.tax_rate = 0.25
    return govt


@pytest.fixture
def central_bank(model):
    return CentralBankAgent(model)


@pytest.fixture
def country(model, govt, central_bank):
    # Given
    return CountrySpace(model, govt, central_bank)


@pytest.fixture
def firm(model):
    # Given
    firm = FirmAgent(model)
    firm.sales = 1000
    firm.productivity = 2
    firm.wage_offer = 20
    firm.inventories = 60
    firm.prev_inventories = 50
    firm.deposit_interest = 30
    firm.loan_interest = 30
    firm.wage_bill = 300
    firm.rd = 100
    return firm


def test_firm_compute_profit_distribution(firm, country):
    # Given
    country.add_tax_payer(firm)

    # When
    firm.compute_profit_distribution()

    # Then
    assert firm.profit == pytest.approx(700)
    assert firm.net_cash_flow == pytest.approx(600)
    assert firm.taxes_payable == pytest.approx(150.0)
    assert firm.dividends_payable == pytest.approx(45.0)


@pytest.fixture
def bank(model):
    # Given
    bank = BankAgent(model)
    bank.loan_interest = 100
    bank.bond_interest = 20
    bank.reserve_interest = 10
    bank.bad_debt = 10
    bank.deposit_interest = 30
    bank.cash_advance_interest = 10
    return bank


def test_bank_compute_profit_distribution(bank, country):
    # Given
    country.add_tax_payer(bank)

    # When
    bank.compute_profit_distribution()

    # Then
    assert bank.profit == pytest.approx(80)
    assert bank.taxes_payable == pytest.approx(20)
    assert bank.dividends_payable == pytest.approx(6)
