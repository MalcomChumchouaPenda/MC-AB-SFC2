import pytest
from networkx import Graph
from agentpy import AgentDList
from unittest.mock import Mock
from model.spaces.economy import Economy

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from model.base import EcoSpace

    # Assert
    assert issubclass(Economy, EcoSpace)


@pytest.fixture
def economy_before_setup():
    # Given
    model = Mock()
    economy = Economy(model)
    return economy


# ---------------------------------------------------
# AGENT BODIES SET TESTS
# ----------------------------------------------------


def test_has_fiscal_authorities_dict(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert economy.fiscal_auths == {}


def test_has_monetary_authorities_dict(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert economy.monetary_auths == {}


def test_has_citizens_list(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert isinstance(economy.citizens, AgentDList)


def test_has_companies_list(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert isinstance(economy.companies, AgentDList)


# ---------------------------------------------------
# ECONOMIC SPACES AND ACCOUNTS SET TESTS
# ----------------------------------------------------


def test_has_accounts_list(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert isinstance(economy.accounts, AgentDList)


def test_has_labor_markets_dict(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert economy.labor_markets == {}


def test_has_good_markets_dict(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert economy.good_markets == {}


def test_has_deposit_markets_dict(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert economy.deposit_markets == {}


def test_has_credit_market_ref(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert economy.credit_market is None


def test_has_bond_market_ref(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert economy.bond_market is None


# ---------------------------------------------------
# DYNAMIC STATE TESTS
# ----------------------------------------------------


def test_has_inflation_prop(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert economy.inflation == 0.0


def test_has_gdp_prop(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert economy.gdp == 0


def test_has_prob_failure_prop(economy_before_setup):
    # Given
    economy = economy_before_setup

    # When
    economy.setup()

    # Then
    assert economy.prob_failure == 0.0


# ---------------------------------------------------
# ROLES MANAGEMENT TESTS
# ----------------------------------------------------


class FakeCitizen(Mock):
    pass


@pytest.fixture
def economy_without_citizens(monkeypatch, economy_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.economy.Citizen", FakeCitizen)
    economy = economy_before_setup
    economy.add_role = Mock()
    economy.citizens = []
    return economy


def test_add_citizen_add_appropriate_role(economy_without_citizens):
    # Given
    household = Mock()
    economy = economy_without_citizens

    # When
    role = economy.add_citizen(household)

    # Then
    economy.add_role.assert_called_with(FakeCitizen, household, "citizen")
    assert role == economy.add_role.return_value


def test_add_citizen_registers_citizen(economy_without_citizens):
    # Given
    household = Mock()
    economy = economy_without_citizens

    # When
    role = economy.add_citizen(household)

    # Then
    assert economy.citizens == [role]


class FakeCompany(Mock):
    pass


@pytest.fixture
def economy_without_companies(monkeypatch, economy_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.economy.Company", FakeCompany)
    economy = economy_before_setup
    economy.add_role = Mock()
    economy.companies = []
    return economy


def test_add_company_add_appropriate_role(economy_without_companies):
    # Given
    agent = Mock()
    economy = economy_without_companies

    # When
    role = economy.add_company(agent, sector="X")

    # Then
    economy.add_role.assert_called_with(FakeCompany, agent, "company")
    assert role == economy.add_role.return_value


def test_add_company_register_company(economy_without_companies):
    # Given
    agent = Mock()
    economy = economy_without_companies

    # When
    role = economy.add_company(agent, sector="X")

    # Then
    assert economy.companies == [role]


def test_add_company_register_sector(economy_without_companies):
    # Given
    agent = Mock()
    economy = economy_without_companies

    # When
    role = economy.add_company(agent, sector="X")

    # Then
    assert role.sector == "X"


# ---------------------------------------------------
# EQUITY INVESTMENT AND DIVIDENDS
# ----------------------------------------------------


@pytest.fixture
def economy_with_company_and_founder(economy_before_setup):
    # Given
    company, founder = Mock(), Mock()
    economy = economy_before_setup
    economy.graph.add_edge(company, founder, share=0)
    return economy, company, founder


def test_fund_company_updates_accounts(economy_with_company_and_founder):
    # Given
    economy, company, founder = economy_with_company_and_founder

    # When
    economy.fund_company(company, founder, 100)

    # Then
    company.account.credit_stock("equities", 100)
    company.account.credit_stock("cash", 100)
    founder.account.debit_stock("equities", 100)
    founder.account.debit_stock("cash", 100)


def test_fund_company_adds_graph_edge(economy_with_company_and_founder):
    # Given
    economy, company, founder = economy_with_company_and_founder
    graph = economy.graph

    # When
    economy.fund_company(company, founder, 100)

    # Then
    assert graph[company][founder]["share"] == 100


def test_fund_company_updates_graph_edge(economy_with_company_and_founder):
    # Given
    economy, company, founder = economy_with_company_and_founder
    economy.graph.add_edge(company, founder, share=50)

    # When
    economy.fund_company(company, founder, 100)

    # Then
    assert economy.graph[company][founder]["share"] == 150


def test_pay_dividends_updates_accounts(economy_with_company_and_founder):
    # Given
    economy, company, founder = economy_with_company_and_founder

    # When
    economy.pay_dividends(company, founder, 10)

    # Then
    company.account.debit_flow("dividends", 10)
    company.account.debit_flow("cash", 10)
    founder.account.credit_flow("dividends", 10)
    founder.account.credit_flow("cash", 10)


# ---------------------------------------------------
# FIRM CREATION TESTS
# ----------------------------------------------------


@pytest.fixture
def economy_before_new_firm(economy_before_setup):
    # Given
    economy = economy_before_setup
    economy.add_company = Mock()
    economy.fund_company = Mock()
    economy.good_markets = {0: Mock(), 1: Mock()}
    economy.labor_markets = {1: Mock()}
    economy.deposit_markets = {1: Mock()}
    economy.credit_market = Mock()
    return economy


@pytest.fixture
def share():
    founder = Mock(resid_equity=10)
    return {"founder": founder, "amount": 5}


@pytest.mark.parametrize("trad, sector", [(True, "FT"), (False, "FNT")])
def test_create_firm_add_and_fund_company(economy_before_new_firm, share, trad, sector):
    # Given
    company = Mock()
    firm = Mock(position=1)
    economy = economy_before_new_firm
    economy.add_company.return_value = company

    # When
    economy.create_firm(firm, [share], tradable=trad)

    # Then
    economy.add_company.assert_called_with(firm, sector=sector)
    economy.fund_company.assert_called_with(company, share["founder"], 5)


def test_create_tradable_firm_in_common_goods_market(economy_before_new_firm, share):
    # Given
    firm = Mock(position=1)
    economy = economy_before_new_firm

    # When
    economy.create_firm(firm, [share], tradable=True)

    # Then
    economy.good_markets[0].add_supplier.assert_called_with(firm)
    economy.good_markets[1].add_supplier.assert_not_called()


def test_create_non_tradable_firm_in_national_goods_market(
    economy_before_new_firm, share
):
    # Given
    firm = Mock(position=1)
    economy = economy_before_new_firm

    # When
    economy.create_firm(firm, [share], tradable=False)

    # Then
    economy.good_markets[0].add_supplier.assert_not_called()
    economy.good_markets[1].add_supplier.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_employer_role(economy_before_new_firm, share, tradable):
    # Given
    firm = Mock(position=1)
    economy = economy_before_new_firm

    # When
    economy.create_firm(firm, [share], tradable=tradable)

    # Then
    economy.labor_markets[1].add_employer.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_borrower_role(economy_before_new_firm, share, tradable):
    # Given
    firm = Mock(position=1)
    economy = economy_before_new_firm

    # When
    economy.create_firm(firm, [share], tradable=tradable)

    # Then
    economy.credit_market.add_borrower.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_depositor_role(economy_before_new_firm, share, tradable):
    # Given
    firm = Mock(position=1)
    economy = economy_before_new_firm

    # When
    economy.create_firm(firm, [share], tradable=tradable)

    # Then
    economy.deposit_markets[1].add_depositor.assert_called_with(firm)


# ---------------------------------------------------
# BANK CREATION TESTS
# ----------------------------------------------------


@pytest.fixture
def economy_before_new_bank(economy_before_setup):
    # Given
    economy = economy_before_setup
    economy.add_company = Mock()
    economy.fund_company = Mock()
    economy.deposit_markets = {1: Mock()}
    economy.credit_market = Mock()
    economy.bond_market = Mock()
    return economy


def test_create_bank_add_and_fund_company(economy_before_new_bank, share):
    # Given
    company = Mock()
    bank = Mock(position=1)
    economy = economy_before_new_bank
    economy.add_company.return_value = company

    # When
    economy.create_bank(bank, [share])

    # Then
    economy.add_company.assert_called_with(bank, sector="B")
    economy.fund_company.assert_called_with(company, share["founder"], 5)


def test_create_bank_add_bond_buyer(economy_before_new_bank, share):
    # Given
    bank = Mock(position=1)
    economy = economy_before_new_bank

    # When
    economy.create_bank(bank, [share])

    # Then
    economy.bond_market.add_buyer.assert_called_with(bank)


def test_create_bank_add_lender_role(economy_before_new_bank, share):
    # Given
    bank = Mock(position=1)
    economy = economy_before_new_bank

    # When
    economy.create_bank(bank, [share])

    # Then
    economy.credit_market.add_lender.assert_called_with(bank)


def test_create_bank_add_bank_role(economy_before_new_bank, share):
    # Given
    bank = Mock(position=1)
    economy = economy_before_new_bank

    # When
    economy.create_bank(bank, [share])

    # Then
    economy.deposit_markets[1].add_bank.assert_called_with(bank)
