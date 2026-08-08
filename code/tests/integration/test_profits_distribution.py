import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import HouseholdAgent, FirmAgent
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


# def test_firm_pay_taxes(firm, household, equity_space):
#     # Given
#     issuer = firm.roles['equity_issuer']
#     holder = household.roles['equity_holder']
#     graph = equity_space.graph
#     graph.add_edge(issuer, holder, share=1.0)

#     # When
#     firm.calc_taxes()
#     firm.calc_dividends()
#     firm.update_net_worth()
#     firm.pay_taxes()
#     firm.pay_dividends()

#     assert firm.taxes_payable == 0
#     assert firm.dividends_payable == 0
#     assert firm.net_worth == 1200
#     taxpayer.pay_tax.assert_called_once_with(100)
#     equity_issuer.distribute_dividends.assert_called_once_with(200)
