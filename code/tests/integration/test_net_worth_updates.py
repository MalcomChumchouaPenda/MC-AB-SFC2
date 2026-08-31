import pytest
from unittest.mock import Mock
from model.spaces.institutionnal import Country
from model.agents.private import Household, Firm, Bank


@pytest.fixture
def model():
    # Given
    model = Mock()
    return model


@pytest.fixture
def household(model):
    # Given
    return Household(model)


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.net_worth = 1000
    firm.net_cash_flow = 500
    firm.taxes_payable = 100
    firm.dividends_payable = 200
    return firm


@pytest.fixture
def country(model):
    # Given
    return Country(model)


def test_firm_update_net_worth(firm, household, country):
    # Given
    holder = country.add_equity_holder(household)
    holder.share = 1.0
    issuer = country.add_equity_issuer(firm)
    country.assign_equity_holder(issuer, holder)

    # When
    firm.update_net_worth()

    # Then
    assert firm.net_worth == 1200
    assert firm.equity == 1200
    assert household.equity == 1200


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    bank.net_worth = 800
    bank.profit = 200
    bank.taxes_payable = 50
    bank.dividends_payable = 50
    return bank


def test_bank_update_net_worth(bank, household, country):
    # Given
    holder = country.add_equity_holder(household)
    holder.share = 1.0
    issuer = country.add_equity_issuer(bank)
    country.assign_equity_holder(issuer, holder)

    # When
    bank.update_net_worth()

    # Then
    assert bank.net_worth == 900
    assert bank.equity == 900
    assert household.equity == 900
