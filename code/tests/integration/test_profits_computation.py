from unittest.mock import Mock
import pytest
from model.spaces.country import Country
from model.agents.bank import Bank
from model.agents.firm import Firm


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.rho = 0.10
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.create_markets()
    return country


@pytest.fixture
def firm(model, country):
    # Given
    firm = Firm(model)
    country.add_firm(firm)
    return firm


@pytest.fixture
def before_firm_computation(firm, country):
    # Given
    firm.roles["producer"].productivity = 2
    firm.roles["producer"].inventories = 60
    firm.account["dep_interests"] = 30
    firm.account["consumption"] = 1000
    firm.account["loan_interests"] = 30
    firm.account["wages"] = 400
    firm.prev_inventories = 50
    firm.wage_offer = 20
    country.tax_rate = 0.25


@pytest.mark.usefixtures("before_firm_computation")
def test_sets_firm_profit(firm):
    # When
    firm.compute_profit_distribution()

    # Then
    assert firm.profit == pytest.approx(700)


@pytest.mark.usefixtures("before_firm_computation")
def test_sets_firm_net_cash_flow(firm):
    # When
    firm.compute_profit_distribution()

    # Then
    assert firm.net_cash_flow == pytest.approx(600)


@pytest.mark.usefixtures("before_firm_computation")
def test_sets_firm_payable_taxes(firm):
    # When
    firm.compute_profit_distribution()

    # Then
    assert firm.taxes_payable == pytest.approx(150.0)


@pytest.mark.usefixtures("before_firm_computation")
def test_sets_firm_payable_dividends(firm):
    # When
    firm.compute_profit_distribution()

    # Then
    assert firm.dividends_payable == pytest.approx(45.0)


@pytest.fixture
def bank(model, country):
    # Given
    bank = Bank(model)
    country.add_bank(bank)
    return bank


@pytest.fixture
def before_bank_computation(bank, country):
    # Given
    bank.account["bond_interests"] = 20
    bank.account["dep_interests"] = 30
    bank.account["loan_interests"] = 100
    bank.account["cash_interests"] = 10
    bank.account["loan_defaults"] = 10
    bank.account["adv_interests"] = 10
    country.tax_rate = 0.25


@pytest.mark.usefixtures("before_bank_computation")
def test_sets_bank_profit(bank):
    # When
    bank.compute_profit_distribution()

    # Then
    assert bank.profit == pytest.approx(80)


@pytest.mark.usefixtures("before_bank_computation")
def test_sets_bank_payable_tax(bank):
    # When
    bank.compute_profit_distribution()

    # Then
    assert bank.taxes_payable == pytest.approx(20)


@pytest.mark.usefixtures("before_bank_computation")
def test_sets_bank_dividends_payable(bank):
    # When
    bank.compute_profit_distribution()

    # Then
    assert bank.dividends_payable == pytest.approx(6)
