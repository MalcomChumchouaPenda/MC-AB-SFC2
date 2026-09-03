import pytest
from agentpy import AgentDList
from unittest.mock import Mock
from model.spaces.monetary_union import MonetaryUnion

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from model.base import EcoSpace

    # Assert
    assert issubclass(MonetaryUnion, EcoSpace)


@pytest.fixture
def union_before_setup():
    # Given
    model = Mock()
    union = MonetaryUnion(model)
    return union


# ---------------------------------------------------
# AGENT BODIES SET TESTS
# ----------------------------------------------------


def test_has_fiscal_authorities_dict(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.fiscal_auths == {}


def test_has_monetary_authorities_dict(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.monetary_auths == {}


def test_has_citizens_list(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert isinstance(union.citizens, AgentDList)


def test_has_companies_list(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert isinstance(union.companies, AgentDList)


# ---------------------------------------------------
# ECONOMIC SPACES SET TESTS
# ----------------------------------------------------


def test_has_labor_markets_dict(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.labor_markets == {}


def test_has_good_markets_dict(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.good_markets == {}


def test_has_deposit_markets_dict(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.deposit_markets == {}


def test_has_credit_market_ref(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.credit_market is None


def test_has_bond_market_ref(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.bond_market is None


# ---------------------------------------------------
# DYNAMIC STATE TESTS
# ----------------------------------------------------


def test_has_inflation_prop(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.inflation == 0.0


def test_has_gdp_prop(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.gdp == 0


def test_has_prob_failure_prop(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.prob_failure == 0.0


# ---------------------------------------------------
# ROLES MANAGEMENT TESTS
# ----------------------------------------------------


class FakeCitizen(Mock):
    pass


@pytest.fixture
def union_without_citizens(monkeypatch, union_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.Citizen", FakeCitizen)
    union = union_before_setup
    union.add_role = Mock()
    union.citizens = []
    return union


def test_add_citizen_add_appropriate_role(union_without_citizens):
    # Given
    household = Mock()
    union = union_without_citizens

    # When
    role = union.add_citizen(household)

    # Then
    union.add_role.assert_called_with(FakeCitizen, household, "citizen")
    assert role == union.add_role.return_value


def test_add_citizen_registers_citizen(union_without_citizens):
    # Given
    household = Mock()
    union = union_without_citizens

    # When
    role = union.add_citizen(household)

    # Then
    assert union.citizens == [role]


class FakeCompany(Mock):
    pass


@pytest.fixture
def union_without_companies(monkeypatch, union_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.Company", FakeCompany)
    union = union_before_setup
    union.add_role = Mock()
    union.companies = []
    return union


def test_add_company_add_appropriate_role(union_without_companies):
    # Given
    agent = Mock()
    union = union_without_companies

    # When
    role = union.add_company(agent, sector="X")

    # Then
    union.add_role.assert_called_with(FakeCompany, agent, "company")
    assert role == union.add_role.return_value


def test_add_company_register_company(union_without_companies):
    # Given
    agent = Mock()
    union = union_without_companies

    # When
    role = union.add_company(agent, sector="X")

    # Then
    assert union.companies == [role]


def test_add_company_register_sector(union_without_companies):
    # Given
    agent = Mock()
    union = union_without_companies

    # When
    role = union.add_company(agent, sector="X")

    # Then
    assert role.sector == "X"


# ---------------------------------------------------
# EQUITY INVESTMENT AND DIVIDENDS
# ----------------------------------------------------


@pytest.fixture
def union_with_company_and_founder(union_before_setup):
    # Given
    company, founder = Mock(), Mock()
    union = union_before_setup
    union.graph.add_edge(company, founder, share=0)
    return union, company, founder


def test_fund_company_updates_accounts(union_with_company_and_founder):
    # Given
    union, company, founder = union_with_company_and_founder

    # When
    union.fund_company(company, founder, 100)

    # Then
    company.account.credit_stock("equities", 100)
    company.account.credit_stock("cash", 100)
    founder.account.debit_stock("equities", 100)
    founder.account.debit_stock("cash", 100)


def test_fund_company_adds_graph_edge(union_with_company_and_founder):
    # Given
    union, company, founder = union_with_company_and_founder
    graph = union.graph

    # When
    union.fund_company(company, founder, 100)

    # Then
    assert graph[company][founder]["share"] == 100


def test_fund_company_updates_graph_edge(union_with_company_and_founder):
    # Given
    union, company, founder = union_with_company_and_founder
    union.graph.add_edge(company, founder, share=50)

    # When
    union.fund_company(company, founder, 100)

    # Then
    assert union.graph[company][founder]["share"] == 150


def test_pay_dividends_updates_accounts(union_with_company_and_founder):
    # Given
    union, company, founder = union_with_company_and_founder

    # When
    union.pay_dividends(company, founder, 10)

    # Then
    company.account.debit_flow("dividends", 10)
    company.account.debit_flow("cash", 10)
    founder.account.credit_flow("dividends", 10)
    founder.account.credit_flow("cash", 10)


# ---------------------------------------------------
# FIRM CREATION TESTS
# ----------------------------------------------------


@pytest.fixture
def union_before_new_firm(union_before_setup):
    # Given
    union = union_before_setup
    union.add_company = Mock()
    union.fund_company = Mock()
    union.good_markets = {0: Mock(), 1: Mock()}
    union.labor_markets = {1: Mock()}
    union.deposit_markets = {1: Mock()}
    union.credit_market = Mock()
    return union


@pytest.fixture
def share():
    founder = Mock(resid_equity=10)
    return {"founder": founder, "amount": 5}


@pytest.mark.parametrize("trad, sector", [(True, "FT"), (False, "FNT")])
def test_create_firm_add_and_fund_company(union_before_new_firm, share, trad, sector):
    # Given
    company = Mock()
    firm = Mock(position=1)
    union = union_before_new_firm
    union.add_company.return_value = company

    # When
    union.create_firm(firm, [share], tradable=trad)

    # Then
    union.add_company.assert_called_with(firm, sector=sector)
    union.fund_company.assert_called_with(company, share["founder"], 5)


def test_create_trad_firm_in_common_goods_market(union_before_new_firm, share):
    # Given
    firm = Mock(position=1)
    union = union_before_new_firm

    # When
    union.create_firm(firm, [share], tradable=True)

    # Then
    union.good_markets[0].add_supplier.assert_called_with(firm)
    union.good_markets[1].add_supplier.assert_not_called()


def test_create_non_trad_firm_in_national_goods_market(union_before_new_firm, share):
    # Given
    firm = Mock(position=1)
    union = union_before_new_firm

    # When
    union.create_firm(firm, [share], tradable=False)

    # Then
    union.good_markets[0].add_supplier.assert_not_called()
    union.good_markets[1].add_supplier.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_employer_role(union_before_new_firm, share, tradable):
    # Given
    firm = Mock(position=1)
    union = union_before_new_firm

    # When
    union.create_firm(firm, [share], tradable=tradable)

    # Then
    union.labor_markets[1].add_employer.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_borrower_role(union_before_new_firm, share, tradable):
    # Given
    firm = Mock(position=1)
    union = union_before_new_firm

    # When
    union.create_firm(firm, [share], tradable=tradable)

    # Then
    union.credit_market.add_borrower.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_depositor_role(union_before_new_firm, share, tradable):
    # Given
    firm = Mock(position=1)
    union = union_before_new_firm

    # When
    union.create_firm(firm, [share], tradable=tradable)

    # Then
    union.deposit_markets[1].add_depositor.assert_called_with(firm)


# ---------------------------------------------------
# BANK CREATION TESTS
# ----------------------------------------------------


@pytest.fixture
def union_before_new_bank(union_before_setup):
    # Given
    union = union_before_setup
    union.add_company = Mock()
    union.fund_company = Mock()
    union.deposit_markets = {1: Mock()}
    union.credit_market = Mock()
    union.bond_market = Mock()
    return union


def test_create_bank_add_and_fund_company(union_before_new_bank, share):
    # Given
    company = Mock()
    bank = Mock(position=1)
    union = union_before_new_bank
    union.add_company.return_value = company

    # When
    union.create_bank(bank, [share])

    # Then
    union.add_company.assert_called_with(bank, sector="B")
    union.fund_company.assert_called_with(company, share["founder"], 5)


def test_create_bank_add_bond_buyer(union_before_new_bank, share):
    # Given
    bank = Mock(position=1)
    union = union_before_new_bank

    # When
    union.create_bank(bank, [share])

    # Then
    union.bond_market.add_buyer.assert_called_with(bank)


def test_create_bank_add_lender_role(union_before_new_bank, share):
    # Given
    bank = Mock(position=1)
    union = union_before_new_bank

    # When
    union.create_bank(bank, [share])

    # Then
    union.credit_market.add_lender.assert_called_with(bank)


def test_create_bank_add_bank_role(union_before_new_bank, share):
    # Given
    bank = Mock(position=1)
    union = union_before_new_bank

    # When
    union.create_bank(bank, [share])

    # Then
    union.deposit_markets[1].add_bank.assert_called_with(bank)
