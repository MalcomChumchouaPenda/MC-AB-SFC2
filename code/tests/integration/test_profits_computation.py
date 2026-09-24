from unittest.mock import Mock
import pytest
from agentpy import Model
from model.base import EcoSpace
from model.agents.bank import Bank
from model.agents.firm import Firm


@pytest.fixture
def model():
    # Given
    model = Model()
    model.p.rho = 0.10
    return model


@pytest.fixture
def space(model):
    # Given
    space = EcoSpace(model)
    return space


@pytest.fixture
def firm(model, space):
    # Given
    firm = Firm(model)
    firm.roles["company"] = Mock()
    firm.roles["producer"] = Mock()
    space.add_account(firm)
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
def bank(model, space):
    # Given
    bank = Bank(model)
    bank.roles["company"] = Mock()
    space.add_account(bank)
    return bank


def test_bank_compute_profit_distribution(bank):
    # Given
    bank.roles["company"].get_tax_rate.return_value = 0.25
    bank.account.flows["bond_interests"] = 20
    bank.account.flows["dep_interests"] = 30
    bank.account.flows["loan_interests"] = 100
    bank.account.flows["cash_interests"] = 10
    bank.account.flows["loan_defaults"] = 10
    bank.account.flows["adv_interests"] = 10

    # When
    bank.compute_profit_distribution()

    # Then
    assert bank.profit == pytest.approx(80)
    assert bank.taxes_payable == pytest.approx(20)
    assert bank.dividends_payable == pytest.approx(6)
