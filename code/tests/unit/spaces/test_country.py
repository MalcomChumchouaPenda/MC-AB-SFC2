import pytest
from unittest.mock import Mock
from model.spaces.country import Country

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.base import EcoSpace

    # When
    is_derived = issubclass(Country, EcoSpace)

    # Then
    assert is_derived


def test_initializes_inflation(fake_model):
    # Given
    model = fake_model

    # When
    country = Country(model)

    # Then
    assert country.inflation == 0


def test_initializes_gdp(fake_model):
    # Given
    model = fake_model

    # When
    country = Country(model)

    # Then
    assert country.gdp == 0


def test_initializes_prob_failure(fake_model):
    # Given
    model = fake_model

    # When
    country = Country(model)

    # Then
    assert country.prob_failure == 0


def test_initializes_tax_rate(fake_model):
    # Given
    model = fake_model

    # When
    country = Country(model)

    # Then
    assert country.tax_rate == 0


def test_initializes_fiscal_authority(fake_model):
    # Given
    model = fake_model

    # When
    country = Country(model)

    # Then
    assert country.fiscal_authority is None


def test_initializes_monetary_authority(fake_model):
    # Given
    model = fake_model

    # When
    country = Country(model)

    # Then
    assert country.monetary_authority is None


# ---------------------------------------------------
# SUB SPACES CREATION
# ----------------------------------------------------


FakeGoodMarket = Mock()
FakeLaborMarket = Mock()
FakeDepositMarket = Mock()


@pytest.fixture
def country_without_markets(monkeypatch, fake_model):
    # Given
    monkeypatch.setattr("model.spaces.country.GoodsMarket", FakeGoodMarket)
    monkeypatch.setattr("model.spaces.country.LaborMarket", FakeLaborMarket)
    monkeypatch.setattr("model.spaces.country.DepositMarket", FakeDepositMarket)
    monkeypatch.setattr(Country, "add_space", Mock())
    country = Country(fake_model)
    return country


def test_create_markets_adds_goods_market(country_without_markets):
    # Given
    country = country_without_markets

    # When
    country.create_markets()

    # Then
    country.add_space.assert_any_call(FakeGoodMarket, "goods_market", tradable=False)


def test_create_markets_adds_labor_market(country_without_markets):
    # Given
    country = country_without_markets

    # When
    country.create_markets()

    # Then
    country.add_space.assert_any_call(FakeLaborMarket, "labor_market")


def test_create_markets_adds_deposit_market(country_without_markets):
    # Given
    country = country_without_markets

    # When
    country.create_markets()

    # Then
    country.add_space.assert_any_call(FakeDepositMarket, "deposit_market")


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


FakeMonetaryAuth = Mock()
FakeFiscalAuth = Mock()
FakeCitizen = Mock()
FakeCompany = Mock()


@pytest.fixture
def country_without_roles(fake_model, monkeypatch):
    # Given
    monkeypatch.setattr("model.spaces.country.MonetaryAuthority", FakeMonetaryAuth)
    monkeypatch.setattr("model.spaces.country.FiscalAuthority", FakeFiscalAuth)
    monkeypatch.setattr("model.spaces.country.Citizen", FakeCitizen)
    monkeypatch.setattr("model.spaces.country.Company", FakeCompany)
    country = Country(fake_model)
    country.add_role = Mock()
    country.env = Mock()
    return country


def test_add_monetary_authority_creates_proper_role(country_without_roles):
    # Given
    cb = Mock()
    country = country_without_roles

    # When
    country.add_monetary_authority(cb)

    # Then
    country.add_role.assert_called_with(FakeMonetaryAuth, cb, "monetary_authority")


def test_add_monetary_authority_registers_authority(country_without_roles):
    # Given
    cb = Mock()
    country = country_without_roles

    # When
    role = country.add_monetary_authority(cb)

    # Then
    assert country.monetary_authority is role


def test_add_monetary_authority_returns_created_role(country_without_roles):
    # Given
    cb = Mock()
    country = country_without_roles

    # When
    role = country.add_monetary_authority(cb)

    # Then
    assert role == country.add_role.return_value


def test_add_fiscal_authority_creates_proper_role(country_without_roles):
    # Given
    govt = Mock()
    country = country_without_roles
    country.monetary_authority = Mock()

    # When
    role = country.add_fiscal_authority(govt)

    # Then
    country.add_role.assert_called_with(FakeFiscalAuth, govt, "fiscal_authority")
    assert role == country.add_role.return_value


def test_add_fiscal_authority_registers_authority(country_without_roles):
    # Given
    govt = Mock()
    country = country_without_roles
    country.monetary_authority = Mock()

    # When
    role = country.add_fiscal_authority(govt)

    # Then
    assert country.fiscal_authority is role


def test_add_fiscal_authority_links_to_cb_id(country_without_roles):
    # Given
    govt = Mock()
    country = country_without_roles
    country.monetary_authority = Mock()

    # When
    country.add_fiscal_authority(govt)

    # Then
    assert govt.cb_id is country.monetary_authority.id


def test_add_fiscal_authority_returns_created_role(country_without_roles):
    # Given
    govt = Mock()
    country = country_without_roles
    country.monetary_authority = Mock()

    # When
    role = country.add_fiscal_authority(govt)

    # Then
    assert role == country.add_role.return_value


def test_add_citizen_creates_proper_role(country_without_roles):
    # Given
    household = Mock()
    country = country_without_roles
    country.monetary_authority = Mock()

    # When
    country.add_citizen(household)

    # Then
    country.add_role.assert_called_with(FakeCitizen, household, "citizen")


def test_add_citizen_links_to_cb_id(country_without_roles):
    # Given
    country = country_without_roles
    country.monetary_authority = Mock(id=5)
    household = Mock()

    # When
    country.add_citizen(household)

    # Then
    assert household.cb_id == 5


def test_add_citizen_returns_created_role(country_without_roles):
    # Given
    household = Mock()
    country = country_without_roles
    country.monetary_authority = Mock()

    # When
    role = country.add_citizen(household)

    # Then
    assert role == country.add_role.return_value


def test_add_company_creates_proper_role(country_without_roles):
    # Given
    agent = Mock()
    country = country_without_roles
    country.monetary_authority = Mock()

    # When
    country.add_company(agent, sector="X")

    # Then
    country.add_role.assert_called_with(FakeCompany, agent, "company")


def test_add_company_register_sector(country_without_roles):
    # Given
    agent = Mock()
    country = country_without_roles
    country.monetary_authority = Mock()

    # When
    role = country.add_company(agent, sector="X")

    # Then
    assert role.sector == "X"


def test_add_company_links_to_cb_id(country_without_roles):
    # Given
    country = country_without_roles
    country.monetary_authority = Mock(id=5)
    agent = Mock()

    # When
    country.add_company(agent, sector="X")

    # Then
    assert agent.cb_id == 5


def test_add_company_returns_created_role(country_without_roles):
    # Given
    agent = Mock()
    country = country_without_roles
    country.monetary_authority = Mock()

    # When
    role = country.add_company(agent, sector="X")

    # Then
    assert role == country.add_role.return_value


# ---------------------------------------------------
# CURRENT INDICATORS
# ----------------------------------------------------


@pytest.fixture
def country_with_roles(country_without_roles):
    # Given
    roles = {}
    country = country_without_roles
    country.roles = roles
    return country, roles


@pytest.fixture
def country_with_two_groups(country_with_roles, make_dlist):
    # Given
    country, roles = country_with_roles
    group1 = make_dlist([Mock(id=i, group="company") for i in range(10)])
    group2 = make_dlist([Mock(id=i, group="company") for i in range(10, 12)])
    roles.update({role.id: role for role in group1 + group2})
    return country, group1, group2


def test_calc_bank_number_ratio(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector = "F"
    group2.sector = "B"

    # When
    ratio = country.calc_bank_number_ratio()

    # Then
    assert ratio == 0.2


def test_calc_bank_number_ratio_if_no_firms(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector = "B"
    group2.sector = "B"

    # When
    ratio = country.calc_bank_number_ratio()

    # Then
    assert ratio == 1.0


def test_calc_bank_equity_ratio(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group1.equity = "F", 50
    group2.sector, group2.equity = "B", 100

    # When
    ratio = country.calc_bank_equity_ratio()

    # Then
    assert ratio == 0.4


def test_calc_bank_equity_ratio_if_no_firms(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group1.equity = "B", 100
    group2.sector, group2.equity = "B", 100

    # When
    ratio = country.calc_bank_equity_ratio()

    # Then
    assert ratio == 1.0


def test_calc_sector_equity_range_for_any_sector(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group1.equity = "X", 100
    group2.sector, group2.equity = "Y", 100
    group2[-1].equity = 200

    # When
    range_ = country.calc_sector_equity_range("Y")

    # Then
    assert range_ == (100, 200)


def test_calc_sector_equity_range_if_empty_sector(country_with_two_groups):
    # Given
    country, group1, group2 = country_with_two_groups
    group1.sector, group1.equity = "X", 100
    group2.sector, group2.equity = "Y", 100

    # When
    range_ = country.calc_sector_equity_range("Z")

    # Then
    assert range_ is None


# ---------------------------------------------------
# EQUITY INVESTMENT
# ----------------------------------------------------


@pytest.fixture
def country_before_transaction(country_without_roles):
    # Given
    country = country_without_roles
    country.transfer_stock = Mock()
    country.make_transaction = Mock()
    return country


def test_pay_public_transfers_updates_accounts(country_before_transaction):
    # Given
    country = country_before_transaction
    citizen = Mock(id=1)
    auth = Mock(id=2)

    # When
    country.pay_public_transfers(auth, citizen, 10)

    # Then
    country.transfer_stock.assert_any_call("cash", 2, 1, 10)
    country.make_transaction.assert_any_call("public_transfers", 2, 1, 10)


@pytest.fixture
def country_with_company_and_founder(country_before_transaction):
    # Given
    company = Mock()
    founder = Mock(resid_equity=0)
    country = country_before_transaction
    country.graph.add_edge(company, founder, value=0)
    return country, company, founder


def test_fund_company_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.fund_company(company, founder, 100)

    # Then
    country.transfer_stock.assert_any_call("cash", founder.id, company.id, 100)
    country.transfer_stock.assert_any_call("equities", company.id, founder.id, 100)


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


def test_pay_taxes_updates_accounts(country_before_transaction):
    # Given
    payer, auth = Mock(), Mock()
    country = country_before_transaction
    country.fiscal_authority = auth

    # When
    country.pay_taxes(payer, 10)

    # Then
    country.transfer_stock.assert_any_call("cash", payer.id, auth.id, 10)
    country.make_transaction.assert_any_call("taxes", payer.id, auth.id, 10)


def test_pay_dividends_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.pay_dividends(company, founder, 10)

    # Then
    country.transfer_stock.assert_any_call("cash", company.id, founder.id, 10)
    country.make_transaction.assert_any_call("dividends", company.id, founder.id, 10)


def test_update_equity_share_updates_accounts(country_with_company_and_founder):
    # Given
    country, company, founder = country_with_company_and_founder

    # When
    country.update_equity_share(company, founder, -10)

    # Then
    country.transfer_stock.assert_any_call("equities", company.id, founder.id, -10)
    country.make_transaction.assert_any_call(
        "profit_transfers", company.id, founder.id, -10
    )


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
def country_before_creation(country_without_roles, make_dlist):
    # Given
    country = country_without_roles
    country.model.firms = make_dlist()
    country.model.banks = make_dlist()
    country.add_company = Mock()
    country.fund_company = Mock()
    country.env = Mock()
    country.spaces["goods_market"] = Mock()
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
    country.spaces["goods_market"].add_producer.assert_not_called()


def test_create_non_trad_firm_in_goods_market(country_before_creation, share):
    # Given
    firm = Mock()
    country = country_before_creation
    market = country.spaces["goods_market"]

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


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_registers_firm(country_before_creation, share, tradable):
    # Given
    firm = Mock()
    country = country_before_creation
    firms = country.model.firms

    # When
    country.create_firm(firm, [share], tradable=tradable)

    # Then
    assert firms[0] is firm


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


def test_create_bank_place_bank_in_env(country_before_creation, share):
    # Given
    country = country_before_creation
    banks = country.model.banks
    bank = Mock()

    # When
    country.create_bank(bank, [share])

    # Then
    assert bank is banks[0]


# ---------------------------------------------------
# TRANSFERS
# ----------------------------------------------------


def test_transfer_profits_to_government(country_before_transaction):
    # Given
    country = country_before_transaction
    country.fiscal_authority = Mock(id=1)
    country.monetary_authority = Mock(id=2)

    # When
    country.transfer_central_bank_profits(100)

    # Then
    country.transfer_stock.assert_any_call("cash", 2, 1, 100)
    country.make_transaction.assert_any_call("profit_transfers", 2, 1, 100)


def test_transfer_residual_cash_of_company(country_before_transaction):
    # Given
    company, founder = Mock(), Mock()
    country = country_before_transaction

    # When
    country.transfer_residual_cash(company, founder, 100)

    # Then
    country.transfer_stock.assert_any_call("cash", company.id, founder.id, 100)
    country.transfer_stock.assert_any_call("equities", founder.id, company.id, 100)


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def country_before_update(country_without_roles):
    # Given
    country = country_without_roles
    country.spaces["goods_market"] = Mock()
    country.roles = {}
    country.gdp = 0
    return country


def test_update_state_updates_gdp(country_before_update):
    # Given
    country = country_before_update
    country.spaces["goods_market"].calc_gdp.return_value = 100

    # When
    country.update_state()

    # Then
    assert country.gdp == 100


def test_update_state_updates_inflation(country_before_update):
    # Given
    country = country_before_update
    country.spaces["goods_market"].calc_inflation.return_value = 0.2

    # When
    country.update_state()

    # Then
    assert country.inflation == 0.2


def test_update_state_updates_prob_failure(country_before_update):
    # Given
    default = Mock(group="company", defaulted=True)
    other = Mock(group="company", defaulted=False)
    country = country_before_update
    country.roles[0] = default
    country.roles[1] = other

    # When
    country.update_state()

    # Then
    assert country.prob_failure == 0.5
