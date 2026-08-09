import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import HouseholdAgent, FirmAgent, GovernmentAgent
from mc_ab_sfc.spaces import CountrySpace, EquitySpace


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.rho = 0.5
    return model


@pytest.fixture
def country(model):
    # Given
    country = CountrySpace(model)
    country.tax_rate = 0.20
    return country


@pytest.fixture
def equity_space(model):
    # Given
    return EquitySpace(model)


@pytest.fixture
def govt(model, country):
    # Given
    govt = GovernmentAgent(model)
    country.add_government(govt)
    return govt


@pytest.fixture
def firm(model, country, equity_space):
    # Given
    firm = FirmAgent(model)
    firm.net_worth = 1000
    firm.net_cash_flow = 500
    firm.cash = 500
    country.add_tax_payer(firm)
    equity_space.add_equity_issuer(firm)
    return firm


@pytest.fixture
def household(model, equity_space):
    # Given
    household = HouseholdAgent(model)
    equity_space.add_equity_holder(household)
    return household


def test_firm_udpate_net_worth(firm, household, equity_space):
    # Given
    issuer = firm.roles["equity_issuer"]
    holder = household.roles["equity_holder"]
    graph = equity_space.graph
    graph.add_edge(issuer, holder, share=1.0)

    # When
    firm.calc_taxes()
    firm.calc_dividends()
    firm.update_net_worth()

    # Then
    assert firm.taxes_payable == 100
    assert firm.dividends_payable == 200
    assert firm.net_worth == 1200
    assert household.equity == 1200


def test_firm_pay_dividends(firm, household, equity_space):
    # Given
    issuer = firm.roles["equity_issuer"]
    holder = household.roles["equity_holder"]
    graph = equity_space.graph
    graph.add_edge(issuer, holder, share=1.0)

    # When
    firm.calc_taxes()
    firm.calc_dividends()
    firm.pay_dividends()

    # Then
    assert firm.dividends_payable == 0
    assert firm.dividends == 200
    assert firm.cash == 300
    assert household.cash == 200
    assert household.dividends == 200


def test_firm_pay_taxes(firm, govt, country):
    # Given
    govt_role = govt.roles['government']
    payer = firm.roles['tax_payer']
    payer.government = govt_role
    graph = country.graph
    graph.add_edge(payer, govt_role)

    # When
    firm.calc_taxes()
    firm.calc_dividends()
    firm.pay_taxes()

    # Then
    assert firm.taxes_payable == 0
    assert firm.taxes == 100
    assert firm.cash == 400
    assert govt.taxes == 100
    assert govt.reserves == 100
