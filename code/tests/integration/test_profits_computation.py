import pytest
from unittest.mock import Mock, PropertyMock
from model.base import EcoAccount
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
def firm(model):
    # Given
    firm = Firm(model)
    firm.setup()
    firm.roles["company"] = Mock()
    firm.roles["producer"] = Mock()
    firm.account = EcoAccount(model)
    firm.account.setup()
    return firm


def test_firm_compute_profit_distribution(firm):
    # Given
    firm.roles["company"].get_tax_rate.return_value = 0.25
    firm.roles["producer"].productivity = 2
    firm.roles["producer"].inventories = 60
    firm.account.flows["dep_interests"] = 30
    firm.account.flows["consumption"] = 1000
    firm.account.flows["loan_interests"] = 30
    firm.account.flows["wages"] = 400
    firm.prev_inventories = 50
    firm.wage_offer = 20

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
    bank = Bank(model)
    bank.setup()
    bank.roles["company"] = Mock()
    bank.account = EcoAccount(model)
    bank.account.setup()
    return bank


def test_bank_compute_profit_distribution(bank):
    # Given
    bank.roles["company"].get_tax_rate.return_value = 0.25
    bank.account.flows["bond_interests"] = 20
    bank.account.flows["dep_interests"] = 30
    bank.account.flows["loan_interests"] = 100
    bank.account.flows["cash_interests"] = 10
    bank.bad_debt = 10
    bank.account.flows["adv_interests"] = 10

    # When
    bank.compute_profit_distribution()

    # Then
    assert bank.profit == pytest.approx(80)
    assert bank.taxes_payable == pytest.approx(20)
    assert bank.dividends_payable == pytest.approx(6)
