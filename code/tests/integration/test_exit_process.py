import pytest
from unittest.mock import Mock
from agentpy import Model
from model.base import EcoAccount
from model.spaces.country import Country
from model.spaces.monetary_union import MonetaryUnion
from model.spaces.credit_market import CreditMarket
from model.spaces.deposit_market import DepositMarket
from model.spaces.bond_market import BondMarket
from model.spaces.good_market import GoodsMarket
from model.spaces.labor_market import LaborMarket
from model.agents.household import Household
from model.agents.firm import Firm
from model.agents.bank import Bank



@pytest.fixture
def model():
    # Given
    model = Model()
    return model

@pytest.fixture
def credit_market(model):
    # Given
    market = CreditMarket(model)
    market.setup()
    return market


@pytest.fixture
def deposit_market(model):
    # Given
    market = DepositMarket(model)
    market.setup()
    return market

@pytest.fixture
def union(model, credit_market):
    # Given
    union = MonetaryUnion(model)
    union.setup()
    union.credit_market = credit_market
    union.monetary_authority = Mock()
    return union

@pytest.fixture
def country(model, union, deposit_market):
    # Given
    country = Country(model)
    country.setup()
    country.union = union
    country.labor_market = Mock()
    country.deposit_market = deposit_market
    country.good_market = Mock()
    country.monetary_authority = Mock()
    return country


@pytest.fixture
def founders(model):
    # Given
    founders = []
    for _ in range(2):
        hh = Household(model)
        hh.setup()
        founders.append(hh)
    return founders


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.setup()
    return firm


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    bank.setup()
    return bank


@pytest.fixture
def country_before_firm_exit(country, firm, founders, bank):
    # Given
    founder1 = country.add_citizen(founders[0])
    founder2 = country.add_citizen(founders[1])
    company1 = country.add_company(firm, "FNT")
    country.add_company(bank, "B")
    country.fund_company(company1, founder1, 500)
    country.fund_company(company1, founder2, 500)
    


@pytest.mark.usefixtures("country_before_firm_exit")
def test_firm_exit_with_residual_cash(firm, founders):
    # Given
    household1, household2 = founders
    
    # When
    firm.exit()

    # Then
    assert firm.account.stocks["cash"] == 0
    assert firm.account.flows["equities"] == 0
    assert household1.account.stocks["cash"] == 500
    assert household1.account.stocks["equities"] == 0
    assert household2.account.stocks["cash"] == 500
    assert household2.account.stocks["equities"] == 0


