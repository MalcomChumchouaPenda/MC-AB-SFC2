import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import HouseholdAgent, FirmAgent, GovernmentAgent
from mc_ab_sfc.spaces import (
    CountrySpace,
    MonetaryUnionSpace,
    LaborMarket,
    DepositMarket,
    CreditMarket,
    GoodsMarket,
)


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.cT = 0.6
    model.p.eta = 0.3
    model.p.initial_equity = 400
    model.firms = []
    return model


@pytest.fixture
def founders(model):
    # Given
    household1 = HouseholdAgent(model)
    household1.desired_equity = 300
    household1.cash = 400
    household2 = HouseholdAgent(model)
    household2.desired_equity = 200
    household2.cash = 400
    return household1, household2

@pytest.fixture
def govt(model):
    govt = GovernmentAgent(model)
    return govt


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnionSpace(model)
    union.markets['goods'] = GoodsMarket(model, tradable=True)
    return union


@pytest.fixture
def country(model, union):
    # Given
    country = CountrySpace(model)
    country.monetary_union = union
    country.markets["goods"] = GoodsMarket(model, tradable=False)
    country.markets["labor"] = LaborMarket(model)
    country.markets["credit"] = CreditMarket(model)
    country.markets["deposit"] = DepositMarket(model)
    return country


def test_household_creates_new_firm(country, founders, govt):
    # Given
    founder1, founder2 = founders
    country.add_equity_holder(founder1)
    country.add_equity_holder(founder2)
    country.markets["deposit"].add_deposit_holder(founder1)
    country.add_government(govt)
    firms = country.model.firms
    graph = country.graph

    # When
    founder1.invest_equity()

    # Then
    assert isinstance(firms[0], FirmAgent)
    assert firms[0].equity == 500
    assert firms[0].cash == 500
    assert founder1.equity == 300
    assert founder1.cash == 100
    assert founder2.equity == 200
    assert founder2.cash == 200
    assert graph.has_edge(founder1.roles['equity_holder'], firms[0].roles['equity_issuer'])
    assert graph.has_edge(founder2.roles['equity_holder'], firms[0].roles['equity_issuer'])


def test_household_creates_no_firm(country, founders, govt):
    # Given
    founder1, _ = founders
    country.add_equity_holder(founder1)
    country.markets["deposit"].add_deposit_holder(founder1)
    country.add_government(govt)
    firms = country.model.firms

    # When
    founder1.invest_equity()

    # Then
    assert len(firms) == 0
    assert founder1.equity == 0
    assert founder1.cash == 400
