import pytest
from agentpy import AgentDList
from unittest.mock import Mock
from model.base import EcoSpace
from model.spaces.country import Country

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Assert
    assert issubclass(Country, EcoSpace)


FakeGoodMarket = Mock()
FakeLaborMarket = Mock()
FakeDepositMarket = Mock()


@pytest.fixture
def country(monkeypatch, fake_model):
    # Given
    monkeypatch.setattr("model.spaces.country.GoodsMarket", FakeGoodMarket)
    monkeypatch.setattr("model.spaces.country.LaborMarket", FakeLaborMarket)
    monkeypatch.setattr("model.spaces.country.DepositMarket", FakeDepositMarket)
    monkeypatch.setattr(Country, "add_space", Mock())
    country = Country(model=fake_model)
    return country


def test_has_inflation(country):
    # Assert
    assert country.inflation == 0


def test_has_gdp(country):
    # Assert
    assert country.gdp == 0


def test_has_prob_failure(country):
    # Assert
    assert country.prob_failure == 0


def test_has_tax_rate(country):
    # Assert
    assert country.tax_rate == 0


def test_has_fiscal_authority_ref(country):
    # Assert
    assert country.fiscal_authority is None


def test_has_monetary_authority_ref(country):
    # Assert
    assert country.monetary_authority is None


# ---------------------------------------------------
# SPACES CREATION
# ----------------------------------------------------


def test_setup_creates_good_market(country):
    # Assert
    country.add_space.assert_any_call(FakeGoodMarket, "good_market", tradable=False)


def test_setup_creates_labor_market(country):
    # Assert
    country.add_space.assert_any_call(FakeLaborMarket, "labor_market")


def test_setup_creates_deposit_market(country):
    # Assert
    country.add_space.assert_any_call(FakeDepositMarket, "deposit_market")


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------

FakeAuthority1 = Mock()
FakeAuthority2 = Mock()
FakeCitizen = Mock()
FakeCompany = Mock()


@pytest.fixture
def country_without_authorities(monkeypatch, country):
    # Given
    monkeypatch.setattr("model.spaces.country.MonetaryAuthority", FakeAuthority1)
    monkeypatch.setattr("model.spaces.country.FiscalAuthority", FakeAuthority2)
    country.add_role = Mock()
    country.env = Mock()
    return country


def test_add_monetary_authority_add_appropriate_role(country_without_authorities):
    # Given
    cb = Mock()
    country = country_without_authorities

    # When
    role = country.add_monetary_authority(cb)

    # Then
    country.add_role.assert_called_with(FakeAuthority1, cb, "monetary_authority")
    assert role == country.add_role.return_value


def test_add_monetary_authority_registers_authority(country_without_authorities):
    # Given
    cb = Mock()
    country = country_without_authorities

    # When
    role = country.add_monetary_authority(cb)

    # Then
    assert country.monetary_authority is role


def test_add_fiscal_authority_add_appropriate_role(country_without_authorities):
    # Given
    govt = Mock()
    country = country_without_authorities
    country.monetary_authority = Mock()

    # When
    role = country.add_fiscal_authority(govt)

    # Then
    country.add_role.assert_called_with(FakeAuthority2, govt, "fiscal_authority")
    assert role == country.add_role.return_value


def test_add_fiscal_authority_registers_authority(country_without_authorities):
    # Given
    govt = Mock()
    country = country_without_authorities
    country.monetary_authority = Mock()

    # When
    role = country.add_fiscal_authority(govt)

    # Then
    assert country.fiscal_authority is role


def test_add_fiscal_authority_links_to_cb_id(country_without_authorities):
    # Given
    govt = Mock()
    country = country_without_authorities
    country.monetary_authority = Mock()

    # When
    country.add_fiscal_authority(govt)

    # Then
    assert govt.cb_id is country.monetary_authority.id


@pytest.fixture
def country_without_citizens(monkeypatch, country):
    # Given
    monkeypatch.setattr("model.spaces.country.Citizen", FakeCitizen)
    country.monetary_authority = Mock()
    country.add_role = Mock()
    country.env = Mock()
    return country


def test_add_citizen_add_appropriate_role(country_without_citizens):
    # Given
    household = Mock()
    country = country_without_citizens

    # When
    role = country.add_citizen(household)

    # Then
    country.add_role.assert_called_with(FakeCitizen, household, "citizen")
    assert role == country.add_role.return_value


def test_add_citizen_links_to_cb_id(country_without_citizens):
    # Given
    country = country_without_citizens
    authority = country.monetary_authority
    household = Mock()

    # When
    country.add_citizen(household)

    # Then
    assert household.cb_id is authority.id


@pytest.fixture
def country_without_companies(monkeypatch, country):
    # Given
    monkeypatch.setattr("model.spaces.country.Company", FakeCompany)
    country.monetary_authority = Mock()
    country.add_role = Mock()
    country.env = Mock()
    return country


def test_add_company_add_appropriate_role(country_without_companies):
    # Given
    agent = Mock()
    country = country_without_companies

    # When
    role = country.add_company(agent, sector="X")

    # Then
    country.add_role.assert_called_with(FakeCompany, agent, "company")
    assert role == country.add_role.return_value


def test_add_company_register_sector(country_without_companies):
    # Given
    agent = Mock()
    country = country_without_companies

    # When
    role = country.add_company(agent, sector="X")

    # Then
    assert role.sector == "X"


def test_add_company_links_to_cb_id(country_without_companies):
    # Given
    country = country_without_companies
    authority = country.monetary_authority
    agent = Mock()

    # When
    country.add_company(agent, sector="X")

    # Then
    assert agent.cb_id is authority.id


# ---------------------------------------------------
# CURRENT INDICATORS
# ----------------------------------------------------


@pytest.fixture
def country_with_companies(country, make_dlist):
    # Given
    companies = make_dlist()
    country.roles = {"company": companies}
    return country, companies


def test_calc_bank_number_ratio(country_with_companies):
    # Given
    country, companies = country_with_companies
    bank_sector = [Mock(sector="B") for _ in range(2)]
    firm_sector = [Mock(sector="F") for _ in range(10)]
    companies.extend(bank_sector + firm_sector)

    # When
    ratio = country.calc_bank_number_ratio()

    # Then
    assert ratio == 0.2


def test_calc_bank_number_ratio_if_no_firms(country_with_companies):
    # Given
    country, companies = country_with_companies
    bank_sector = [Mock(sector="B") for _ in range(2)]
    companies.extend(bank_sector)

    # When
    ratio = country.calc_bank_number_ratio()

    # Then
    assert ratio == 1.0


def test_calc_bank_equity_ratio(country_with_companies):
    # Given
    country, companies = country_with_companies
    bank_sector = [Mock(sector="B", equity=100) for _ in range(2)]
    firm_sector = [Mock(sector="F", equity=50) for _ in range(10)]
    companies.extend(bank_sector + firm_sector)

    # When
    ratio = country.calc_bank_equity_ratio()

    # Then
    assert ratio == 0.4


def test_calc_bank_equity_ratio_if_no_firms(country_with_companies):
    # Given
    country, companies = country_with_companies
    bank_sector = [Mock(sector="B", equity=100) for _ in range(2)]
    companies.extend(bank_sector)

    # When
    ratio = country.calc_bank_equity_ratio()

    # Then
    assert ratio == 1.0


def test_calc_sector_equity_range_for_any_sector(country_with_companies):
    # Given
    country, companies = country_with_companies
    target_companies = [Mock(sector="X", equity=100 * i) for i in range(2, 5)]
    other_companies = [Mock(sector="Y", equity=100 * i) for i in range(1, 6)]
    companies.extend(target_companies + other_companies)

    # When
    range_ = country.calc_sector_equity_range("X")

    # Then
    assert range_ == (200, 400)


def test_calc_sector_equity_range_if_empty_sector(country_with_companies):
    # Given
    country, companies = country_with_companies
    companies.extend([Mock(sector="Y", equity=100)])

    # When
    range_ = country.calc_sector_equity_range("X")

    # Then
    assert range_ is None


# ---------------------------------------------------
# EQUITY INVESTMENT
# ----------------------------------------------------


@pytest.fixture
def country_with_citizens(country, make_dlist):
    # Given
    citizens = [Mock(resid_equity=100) for _ in range(2)]
    citizens = make_dlist(citizens)
    country.roles = {"citizen": citizens}
    country.transfer_stock = Mock()
    country.record_flow = Mock()
    return country, citizens


def test_pay_public_transfers_updates_accounts(country_with_citizens):
    # Given
    country, citizens = country_with_citizens
    transfer_stock = country.transfer_stock
    record_flow = country.record_flow
    auth = Mock()

    # When
    country.pay_public_transfers(auth, citizens[0], 10)

    # Then
    transfer_stock.assert_any_call("cash", auth.id, citizens[0].id, 10)
    record_flow.assert_any_call("public_transfers", auth.id, citizens[0].id, 10)


@pytest.fixture
def country_with_company_and_founder(country):
    # Given
    company = Mock()
    founder = Mock(resid_equity=0)
    country.graph.add_edge(company, founder, value=0)
    country.transfer_stock = Mock()
    country.record_flow = Mock()
    return country, company, founder


def test_fund_company_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    transfer_stock = country.transfer_stock

    # When
    country.fund_company(company, founder, 100)

    # Then
    transfer_stock.assert_any_call("cash", founder.id, company.id, 100)
    transfer_stock.assert_any_call("equities", company.id, founder.id, 100)


def test_fund_company_adds_graph_edge(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    graph = country.graph
    graph.remove_edge(company, founder)

    # When
    country.fund_company(company, founder, 100)

    # Then
    assert graph[company][founder]["value"] == 100


def test_fund_company_updates_graph_edge(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    country.graph.add_edge(company, founder, value=50)

    # When
    country.fund_company(company, founder, 100)

    # Then
    assert country.graph[company][founder]["value"] == 150


def test_fund_company_reduces_resid_equity(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    founder.resid_equity = 150

    # When
    country.fund_company(company, founder, 100)

    # Then
    assert founder.resid_equity == 50


# ---------------------------------------------------
#  DIVIDENDS AND TAXES
# ----------------------------------------------------


def test_pay_dividends_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    transfer_stock = country.transfer_stock
    record_flow = country.record_flow

    # When
    country.pay_dividends(company, founder, 10)

    # Then
    transfer_stock.assert_any_call("cash", company.id, founder.id, 10)
    record_flow.assert_any_call("dividends", company.id, founder.id, 10)


def test_pay_taxes_updates_accounts(country):
    # Given
    payer, auth = Mock(), Mock()
    country.fiscal_authority = auth
    transfer_stock = country.transfer_stock = Mock()
    record_flow = country.record_flow = Mock()

    # When
    country.pay_taxes(payer, 10)

    # Then
    transfer_stock.assert_any_call("cash", payer.id, auth.id, 10)
    record_flow.assert_any_call("taxes", payer.id, auth.id, 10)


def test_update_equity_share_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder
    transfer_stock = country.transfer_stock
    record_flow = country.record_flow

    # When
    country.update_equity_share(company, founder, -10)

    # Then
    transfer_stock.assert_any_call("equities", company.id, founder.id, -10)
    record_flow.assert_any_call("profit_transfers", company.id, founder.id, -10)


def test_update_equity_share_updates_graph_edge(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.update_equity_share(company, founder, -10)

    # Then
    assert country.graph[company][founder]["value"] == -10


# ---------------------------------------------------
# FIRM CREATION
# ----------------------------------------------------


@pytest.fixture
def country_before_creation(country):
    # Given
    country.add_company = Mock()
    country.fund_company = Mock()
    country.env = Mock()
    country.spaces["good_market"] = Mock()
    country.spaces["labor_market"] = Mock()
    country.spaces["deposit_market"] = Mock()
    return country


@pytest.fixture
def share():
    founder = Mock(resid_equity=10)
    return {"founder": founder, "amount": 5}


@pytest.mark.parametrize("trad, sector", [(True, "FT"), (False, "FNT")])
def test_create_firm_add_and_fund_company(country_before_creation, share, trad, sector):
    # Given
    firm = Mock()
    company = Mock()
    country = country_before_creation
    country.add_company.return_value = company

    # When
    country.create_firm(firm, [share], tradable=trad)

    # Then
    country.add_company.assert_called_with(firm, sector=sector)
    country.fund_company.assert_called_with(company, share["founder"], 5)


def test_dont_create_trad_firm_in_goods_market(country_before_creation, share):
    # Given
    firm = Mock()
    country = country_before_creation

    # When
    country.create_firm(firm, [share], tradable=True)

    # Then
    country.spaces["good_market"].add_producer.assert_not_called()


def test_create_non_trad_firm_in_goods_market(country_before_creation, share):
    # Given
    firm = Mock()
    country = country_before_creation
    market = country.spaces["good_market"]

    # When
    country.create_firm(firm, [share], tradable=False)

    # Then
    market.add_producer.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_employer_role(country_before_creation, share, tradable):
    # Given
    firm = Mock()
    country = country_before_creation
    market = country.spaces["labor_market"]

    # When
    country.create_firm(firm, [share], tradable=tradable)

    # Then
    market.add_employer.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_add_depositor_role(country_before_creation, share, tradable):
    # Given
    firm = Mock()
    country = country_before_creation
    market = country.spaces["deposit_market"]

    # When
    country.create_firm(firm, [share], tradable=tradable)

    # Then
    market.add_depositor.assert_called_with(firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_place_firm_in_env(country_before_creation, share, tradable):
    # Given
    firm = Mock()
    country = country_before_creation

    # When
    country.create_firm(firm, [share], tradable=tradable)

    # Then
    country.env.place_firm.assert_called_with(firm, tradable=tradable)


# ---------------------------------------------------
# BANK CREATION
# ----------------------------------------------------


def test_create_bank_add_and_fund_company(country_before_creation, share):
    # Given
    bank = Mock()
    company = Mock()
    country = country_before_creation
    country.add_company.return_value = company

    # When
    country.create_bank(bank, [share])

    # Then
    country.add_company.assert_called_with(bank, sector="B")
    country.fund_company.assert_called_with(company, share["founder"], 5)


def test_create_bank_add_deposit_bank_role(country_before_creation, share):
    # Given
    bank = Mock()
    country = country_before_creation
    market = country.spaces["deposit_market"]

    # When
    country.create_bank(bank, [share])

    # Then
    market.add_deposit_bank.assert_called_with(bank)


def test_create_bank_place_bank_in_env(country_before_creation, share):
    # Given
    bank = Mock()
    country = country_before_creation

    # When
    country.create_bank(bank, [share])

    # Then
    country.env.place_bank.assert_called_with(bank)


# ---------------------------------------------------
# TRANSFERS
# ----------------------------------------------------


@pytest.fixture
def country_before_transfers(country):
    # Given
    country.transfer_stock = Mock()
    country.record_flow = Mock()
    return country


def test_transfer_profits_to_government(country_before_transfers):
    # Given
    auth1, auth2 = Mock(), Mock()
    country = country_before_transfers
    country.fiscal_authority = auth1
    country.monetary_authority = auth2
    transfer_stock = country.transfer_stock
    record_flow = country.record_flow

    # When
    country.transfer_central_bank_profits(100)

    # Then
    transfer_stock.assert_any_call("cash", auth2.id, auth1.id, 100)
    record_flow.assert_any_call("profit_transfers", auth2.id, auth1.id, 100)


def test_transfer_residual_cash_of_company(country_before_transfers):
    # Given
    company, founder = Mock(), Mock()
    country = country_before_transfers
    transfer_stock = country.transfer_stock

    # When
    country.transfer_residual_cash(company, founder, 100)

    # Then
    transfer_stock.assert_any_call("cash", company.id, founder.id, 100)
    transfer_stock.assert_any_call("equities", founder.id, company.id, 100)


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def country_before_update(country, make_dlist):
    # Given
    country.spaces["good_market"] = Mock()
    country.roles = {"company": make_dlist()}
    country.gdp = 0
    return country


def test_update_state_updates_gdp(country_before_update):
    # Given
    country = country_before_update
    country.spaces["good_market"].calc_gdp.return_value = 100

    # When
    country.update_state()

    # Then
    assert country.gdp == 100


def test_update_state_updates_inflation(country_before_update):
    # Given
    country = country_before_update
    country.spaces["good_market"].calc_inflation.return_value = 0.2

    # When
    country.update_state()

    # Then
    assert country.inflation == 0.2


def test_update_state_updates_prob_failure(country_before_update):
    # Given
    defaults = [Mock(defaulted=True) for _ in range(5)]
    others = [Mock(defaulted=False) for _ in range(5)]
    country = country_before_update
    country.roles["company"].extend(defaults + others)

    # When
    country.update_state()

    # Then
    assert country.prob_failure == 0.5
