import pytest
from unittest.mock import Mock, PropertyMock
from mc_ab_sfc.agents import Household, Firm, Bank, Government, NationalCentralBank
from mc_ab_sfc.spaces import (
    Country,
    LaborMarket,
    DepositMarket,
    CreditMarket,
    GoodsMarket,
    BondMarket,
)


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.cT = 0.6
    model.p.eta = 0.3
    model.p.initial_equity = 400
    model.firms = []
    model.banks = []
    return model


@pytest.fixture
def founders(model):
    # Given
    household1 = Household(model)
    household1.desired_equity = 300
    household1.cash = 400
    household2 = Household(model)
    household2.desired_equity = 200
    household2.cash = 400
    return household1, household2


@pytest.fixture
def govt(model):
    govt = Government(model)
    return govt


@pytest.fixture
def bank(model):
    return Bank(model)


@pytest.fixture
def cb(model):
    # Given
    cb = NationalCentralBank(model)
    cb.setup()
    return cb


@pytest.fixture
def bond_market(model):
    bond_market = BondMarket(model)
    bond_market.setup()
    model.bond_market = bond_market
    return bond_market


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.markets["goods"] = GoodsMarket(model, tradable=False)
    country.markets["labor"] = LaborMarket(model)
    country.markets["credit"] = CreditMarket(model)
    country.markets["deposit"] = DepositMarket(model)
    country.markets["deposit"].setup()
    return country


def test_household_creates_new_firm(country, founders, govt):
    # Given
    founder1, founder2 = founders
    holder1 = country.add_equity_holder(founder1)
    holder2 = country.add_equity_holder(founder2)
    country.markets["deposit"].add_client(founder1)
    firms = country.model.firms
    graph = country.graph

    # TODO
    # # When
    # founder1.invest_equity()

    # # Then
    # assert isinstance(firms[0], Firm)
    # assert firms[0].equity == 500
    # assert firms[0].cash == 500
    # assert founder1.equity == 300
    # assert founder1.cash == 100
    # assert founder2.equity == 200
    # assert founder2.cash == 200
    # assert graph.has_edge(holder1, firms[0].roles["equity_issuer"])
    # assert graph.has_edge(holder2, firms[0].roles["equity_issuer"])


def test_household_creates_no_firm(country, founders, govt):
    # Given
    founder, _ = founders
    country.add_equity_holder(founder)
    deposit_market = country.markets["deposit"]
    deposit_market.add_client(founder)
    firms = country.model.firms

    # TODO
    # # When
    # founder.invest_equity()

    # # Then
    # assert len(firms) == 0
    # assert founder.equity == 0
    # assert founder.cash == 400


@pytest.mark.usefixtures("bond_market")
def test_household_creates_new_bank(country, founders, govt):
    # Given
    founder1, founder2 = founders
    holder1 = country.add_equity_holder(founder1)
    holder2 = country.add_equity_holder(founder2)
    country.markets["deposit"].add_client(founder1)
    country.firm_roles = [Mock(equity=100) for _ in range(5)]
    banks = country.model.banks
    graph = country.graph

    # TODO
    # # When
    # founder1.invest_equity()

    # # Then
    # assert isinstance(banks[0], Bank)
    # assert banks[0].equity == 500
    # assert banks[0].reserves == 500
    # assert founder1.equity == 300
    # assert founder1.cash == 100
    # assert founder2.equity == 200
    # assert founder2.cash == 200
    # assert graph.has_edge(holder1, banks[0].roles["equity_issuer"])
    # assert graph.has_edge(holder2, banks[0].roles["equity_issuer"])


def test_household_creates_no_bank(country, founders, govt):
    # Given
    founder, _ = founders
    country.add_equity_holder(founder)
    country.firm_roles = [Mock(equity=100) for _ in range(5)]
    deposit_market = country.markets["deposit"]
    deposit_market.add_client(founder)
    banks = country.model.banks

    # TODO
    # # When
    # founder.invest_equity()

    # # Then
    # assert len(banks) == 0
    # assert founder.equity == 0
    # assert founder.cash == 400


def test_household_makes_deposits_with_residual_cash(country, founders, bank, govt):
    # Given
    founder, _ = founders
    country.add_equity_holder(founder)
    deposit_market = country.markets["deposit"]
    # bank_role = deposit_market.add_bank(bank)
    # holder_role = deposit_market.add_client(founder)
    # deposit_market.open_account(holder_role, bank_role)

    # TODO
    # # When
    # founder.invest_equity()

    # # Then
    # assert founder.equity == 0
    # assert founder.cash == 0
    # assert founder.deposits == 400
    # assert bank.reserves == 400
    # assert bank.deposits == 400
