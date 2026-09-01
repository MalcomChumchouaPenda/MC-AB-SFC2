import pytest
from unittest.mock import Mock, PropertyMock
from model.spaces.institutionnal import Country
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.agents.government import Government


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.rho = 0.10
    return model


@pytest.fixture
def govt(model):
    # Given
    govt = Government(model)
    govt.tax_rate = 0.25
    model.governments = {"any": govt}
    return govt


@pytest.fixture
def firm(model, monkeypatch):
    # Given
    monkeypatch.setattr(Firm, "dep_interests", PropertyMock(return_value=30))
    firm = Firm(model)
    firm.country = "any"
    firm.sales = 1000
    firm.productivity = 2
    firm.wage_offer = 20
    firm.inventories = 60
    firm.prev_inventories = 50
    firm.loan_interest = 30
    firm.wage_bill = 300
    firm.rd = 100
    return firm


def test_firm_compute_profit_distribution(firm, govt):
    # When
    firm.compute_profit_distribution()

    # Then
    assert govt.taxes == 0
    assert firm.profit == pytest.approx(700)
    assert firm.net_cash_flow == pytest.approx(600)
    assert firm.taxes_payable == pytest.approx(150.0)
    assert firm.dividends_payable == pytest.approx(45.0)


@pytest.fixture
def bank(model, monkeypatch):
    # Given
    monkeypatch.setattr(Bank, "bond_interests", PropertyMock(return_value=20))
    monkeypatch.setattr(Bank, "dep_interests", PropertyMock(return_value=30))
    bank = Bank(model)
    bank.country = "any"
    bank.loan_interest = 100
    bank.reserve_interest = 10
    bank.bad_debt = 10
    bank.cash_advance_interest = 10
    return bank


def test_bank_compute_profit_distribution(bank, govt):
    # When
    bank.compute_profit_distribution()

    # Then
    assert govt.taxes == 0
    assert bank.profit == pytest.approx(80)
    assert bank.taxes_payable == pytest.approx(20)
    assert bank.dividends_payable == pytest.approx(6)
