import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import HouseholdAgent, FirmAgent
from mc_ab_sfc.spaces import EquitySpace


@pytest.fixture
def model():
    # Given
    model = Mock()
    return model

@pytest.fixture
def firm(model):
    # Given
    firm = FirmAgent(model)
    firm.net_worth = 1000
    firm.net_cash_flow = 500
    firm.taxes_payable = 100
    firm.dividends_payable = 200
    return firm

@pytest.fixture
def household(model):
    # Given
    return HouseholdAgent(model)


@pytest.fixture
def equity_space(model):
    # Given
    return EquitySpace(model)


def test_firm_udpate_net_worth(firm, household, equity_space):
    # Given
    issuer = equity_space.add_equity_issuer(firm)
    holder = equity_space.add_equity_holder(household)
    equity_space.assign_equity_holder(holder, issuer, 1.0)

    # When
    firm.update_net_worth()

    # Then
    assert firm.net_worth == 1200
    assert firm.equity == 1200
    assert household.equity == 1200
