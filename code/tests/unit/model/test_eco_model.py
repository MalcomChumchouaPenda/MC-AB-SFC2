import pytest
from unittest.mock import Mock
from model.model import EcoModel

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_agentpy_model():
    # Given
    from agentpy import Model

    # When
    is_derived = issubclass(EcoModel, Model)

    # Then
    assert is_derived


# ---------------------------------------------------
# SETUP PROCESS
# ----------------------------------------------------


@pytest.fixture
def params():
    return {
        "country_number": 2,
        "household_number": 10,
        "psi": 10,
        "upsilon": 1.0,
        "initial_wage": 1.0,
        "initial_productivity": 1.0,
        "initial_tax_rate": 0.4,
        "cy": 0.9,
        "cd": 0.2,
        "delta": 0.03,
        "cT": 0.4,
        "beta": 2.0,
        "lambda_": 0.2,
        "theta": 0.2,
        "gamma": 0.03,
        "nu": 1.5,
        "rho": 0.95,
        "zeta": 0.1,
        "mu1": 20,
        "mu2": 0.1,
        "iota_l": 1.0,
        "chi": 0.003,
        "iota_b": 0.1,
        "initial_discount_rate": 0.0,
        "initial_bond_rate": 0.001,
        "long_run_rate": 0.0075,
        "xi": 0.8,
        "xi_deltap": 2,
        "inflation_target": 0.005,
        "dmax": 0.03,
        "tax_min": 0.35,
        "tax_max": 0.45,
        "g_min": 0.4,
        "g_max": 0.6,
        "eta": 0.03,
        "initial_equity": 10.0,
    }


FakeDList = Mock()


@pytest.fixture
def before_setup_call(monkeypatch):
    # Given
    monkeypatch.setattr("model.model.AgentDList", FakeDList)
    monkeypatch.setattr(EcoModel, "_create_union", Mock())
    monkeypatch.setattr(EcoModel, "_create_households", Mock())
    monkeypatch.setattr(EcoModel, "_create_governments", Mock())
    monkeypatch.setattr(EcoModel, "_create_central_banks", Mock())


@pytest.mark.usefixtures("before_setup_call")
def test_setup_by_calling_four_sub_procedures(params):
    # Given
    model = EcoModel(params)

    # When
    model.setup()

    # Then
    model._create_union.assert_called_once_with()
    model._create_households.assert_called_once_with()
    model._create_governments.assert_called_once_with()
    model._create_central_banks.assert_called_once_with()


@pytest.mark.usefixtures("before_setup_call")
def test_setup_creates_firms_as_empty_agent_dlist(params):
    # Given
    model = EcoModel(params)

    # When
    model.setup()

    # Then
    assert model.firms == FakeDList.return_value


@pytest.mark.usefixtures("before_setup_call")
def test_setup_creates_banks_as_empty_agent_dlist(params):
    # Given
    model = EcoModel(params)

    # When
    model.setup()

    # Then
    assert model.banks == FakeDList.return_value


def test_create_union_creates_monetary_union(monkeypatch, params):
    # Given
    FakeUnion = Mock()
    monkeypatch.setattr("model.model.MonetaryUnion", FakeUnion)
    model = EcoModel(params)

    # When
    model._create_union()

    # Then
    FakeUnion.assert_called_once_with(model)
    assert model.union is FakeUnion.return_value


def test_create_union_creates_markets(monkeypatch, params):
    # Given
    union = Mock()
    FakeUnion = Mock(return_value=union)
    monkeypatch.setattr("model.model.MonetaryUnion", FakeUnion)
    model = EcoModel(params)

    # When
    model._create_union()

    # Then
    union.create_markets.assert_called_with()


def test_create_union_creates_countries(monkeypatch, params):
    # Given
    union = Mock()
    FakeUnion = Mock(return_value=union)
    monkeypatch.setattr("model.model.MonetaryUnion", FakeUnion)
    model = EcoModel(params)

    # When
    model._create_union()

    # Then
    union.create_countries.assert_called_with(params["country_number"])


FakeList = Mock()
FakeIter = Mock()
FakeHousehold = Mock()


@pytest.fixture
def before_household_creation(monkeypatch):
    # Given
    monkeypatch.setattr("model.model.AgentList", FakeList)
    monkeypatch.setattr("model.model.Household", FakeHousehold)
    monkeypatch.setattr("model.model.AttrIter", FakeIter)


@pytest.mark.usefixtures("before_household_creation")
def test_create_households_creates_households_agent_list(params):
    # Given
    num1 = params["household_number"]
    num2 = params["country_number"]
    model = EcoModel(params)
    model.union = Mock()

    # When
    model._create_households()

    # Then
    FakeList.assert_called_with(model, num1 * num2, FakeHousehold)
    assert model.households is FakeList.return_value


@pytest.mark.usefixtures("before_household_creation")
def test_create_households_sets_households_country_pos(params):
    # Given
    num1 = params["household_number"]
    num2 = params["country_number"]
    model = EcoModel(params)
    model.union = Mock()

    # When
    model._create_households()

    # Then
    FakeIter.assert_called_with(list(range(num2)) * num1)
    assert model.households.country_pos is FakeIter.return_value


@pytest.mark.usefixtures("before_household_creation")
def test_create_households_adds_households_to_union(params):
    # Given
    union = Mock()
    agent_list = Mock()
    FakeList.return_value = agent_list
    model = EcoModel(params)
    model.union = union

    # When
    model._create_households()

    # Then
    union.add_agents.assert_called_with(agent_list)


FakeGovt = Mock()


@pytest.fixture
def before_govt_creation(monkeypatch):
    # Given
    monkeypatch.setattr("model.model.AgentList", FakeList)
    monkeypatch.setattr("model.model.Government", FakeGovt)
    monkeypatch.setattr("model.model.AttrIter", FakeIter)


@pytest.mark.usefixtures("before_govt_creation")
def test_create_governments_creates_govt_agent_list(params):
    # Given
    num = params["country_number"]
    model = EcoModel(params)
    model.union = Mock()

    # When
    model._create_governments()

    # Then
    FakeList.assert_called_with(model, num, FakeGovt)
    assert model.governments is FakeList.return_value


@pytest.mark.usefixtures("before_govt_creation")
def test_create_governments_sets_govts_with_country_pos(params):
    # Given
    num = params["country_number"]
    model = EcoModel(params)
    model.union = Mock()

    # When
    model._create_governments()

    # Then
    FakeIter.assert_called_with(list(range(num)))
    assert model.governments.country_pos is FakeIter.return_value


@pytest.mark.usefixtures("before_govt_creation")
def test_create_governments_adds_governments_to_union(params):
    # Given
    union = Mock()
    agent_list = Mock()
    FakeList.return_value = agent_list
    model = EcoModel(params)
    model.union = union

    # When
    model._create_governments()

    # Then
    union.add_agents.assert_called_with(agent_list)


FakeCBank = Mock()


@pytest.fixture
def before_cbank_creation(monkeypatch):
    # Given
    monkeypatch.setattr("model.model.AgentList", FakeList)
    monkeypatch.setattr("model.model.CentralBank", FakeCBank)
    monkeypatch.setattr("model.model.AttrIter", FakeIter)


@pytest.mark.usefixtures("before_cbank_creation")
def test_create_central_banks_creates_national_cbs_as_agent_list(params):
    # Given
    num = params["country_number"]
    model = EcoModel(params)
    model.union = Mock()

    # When
    model._create_central_banks()

    # Then
    FakeList.assert_called_with(model, num, FakeCBank)
    assert model.national_central_banks is FakeList.return_value


@pytest.mark.usefixtures("before_cbank_creation")
def test_create_central_banks_creates_union_cb(params):
    # Given
    model = EcoModel(params)
    model.union = Mock()

    # When
    model._create_central_banks()

    # Then
    FakeCBank.assert_called_with(model)
    assert model.union_central_bank is FakeCBank.return_value


@pytest.mark.usefixtures("before_cbank_creation")
def test_create_central_banks_sets_national_cbs_country_pos(params):
    # Given
    num = params["country_number"]
    model = EcoModel(params)
    model.union = Mock()

    # When
    model._create_central_banks()

    # Then
    FakeIter.assert_called_with(list(range(num)))
    assert model.national_central_banks.country_pos is FakeIter.return_value


@pytest.mark.usefixtures("before_cbank_creation")
def test_create_central_banks_sets_cbs_national_property(params):
    # Given
    model = EcoModel(params)
    model.union = Mock()

    # When
    model._create_central_banks()

    # Then
    assert model.union_central_bank.national == False
    assert model.national_central_banks.national == True


@pytest.mark.usefixtures("before_cbank_creation")
def test_create_central_banks_adds_national_cbs_to_union(params):
    # Given
    union = Mock()
    agent_list = Mock()
    FakeList.return_value = agent_list
    model = EcoModel(params)
    model.union = union

    # When
    model._create_central_banks()

    # Then
    union.add_agents.assert_any_call(agent_list)


@pytest.mark.usefixtures("before_cbank_creation")
def test_create_central_banks_adds_union_cb_to_union(params):
    # Given
    union = Mock()
    cb = Mock()
    FakeCBank.return_value = cb
    model = EcoModel(params)
    model.union = union

    # When
    model._create_central_banks()

    # Then
    union.add_agents.assert_any_call([cb])


# ---------------------------------------------------
# STEP PROCESS
# ----------------------------------------------------


@pytest.fixture
def before_step_call(monkeypatch):
    # Given
    monkeypatch.setattr(EcoModel, "_production_and_rd_planning", Mock())
    monkeypatch.setattr(EcoModel, "_credit_markets_matching", Mock())
    monkeypatch.setattr(EcoModel, "_labor_markets_matching", Mock())
    monkeypatch.setattr(EcoModel, "_production_and_incomes_distribution", Mock())
    monkeypatch.setattr(EcoModel, "_tax_collection_and_public_expenditures", Mock())
    monkeypatch.setattr(EcoModel, "_bond_markets_matching", Mock())
    monkeypatch.setattr(EcoModel, "_goods_consumption", Mock())
    monkeypatch.setattr(EcoModel, "_profit_distribution_planning", Mock())
    monkeypatch.setattr(EcoModel, "_enter_exit", Mock())


@pytest.mark.usefixtures("before_step_call")
def test_step_by_calling_nine_sub_procedures(params):
    # Given
    model = EcoModel(params)

    # When
    model.step()

    # Then
    model._production_and_rd_planning.assert_called_with()
    model._credit_markets_matching.assert_called_with()
    model._labor_markets_matching.assert_called_with()
    model._production_and_incomes_distribution.assert_called_with()
    model._tax_collection_and_public_expenditures.assert_called_with()
    model._bond_markets_matching.assert_called_with()
    model._goods_consumption.assert_called_with()
    model._profit_distribution_planning.assert_called_with()
    model._enter_exit.assert_called_with()


def test_production_and_rd_planning(params):
    # Given
    model = EcoModel(params)
    model.firms = Mock()

    # When
    model._production_and_rd_planning()

    # Then
    model.firms.plan_production.assert_called_with()
    model.firms.adapt_expectations.assert_called_with()
    model.firms.revise_wage_offer.assert_called_with()


def test_credit_markets_matching(params):
    # Given
    model = EcoModel(params)
    model.firms = Mock()
    model.banks = Mock()

    # When
    model._credit_markets_matching()

    # Then
    model.firms.request_loans.assert_called_with()
    model.banks.grant_loans.assert_called_with()
    model.banks.request_cash_advances.assert_called_with()


def test_labor_markets_matching(params):
    # Given
    model = EcoModel(params)
    model.households = Mock()

    # When
    model._labor_markets_matching()

    # Then
    model.households.revise_reservation_wage.assert_called_with()
    model.households.search_jobs.assert_called_with()


def test_production_and_incomes_distribution(params):
    # Given
    model = EcoModel(params)
    model.firms = Mock()
    model.banks = Mock()

    # When
    model._production_and_incomes_distribution()

    # Then
    model.firms.pay_wages.assert_called_with()
    model.firms.produce_goods.assert_called_with()
    model.firms.update_productivity.assert_called_with()
    model.firms.pay_dividends.assert_called_with()
    model.banks.pay_deposit_interests.assert_called_with()
    model.banks.pay_dividends.assert_called_with()


def test_tax_collection_and_public_expenditures(params):
    # Given
    model = EcoModel(params)
    model.households = Mock()
    model.firms = Mock()
    model.banks = Mock()
    model.governments = Mock()

    # When
    model._tax_collection_and_public_expenditures()

    # Then
    model.households.pay_taxes.assert_called_with()
    model.firms.pay_taxes.assert_called_with()
    model.banks.pay_taxes.assert_called_with()
    model.governments.calc_budget_balance.assert_called_with()
    model.governments.update_fiscal_policy.assert_called_with()
    model.governments.repay_bonds.assert_called_with()
    model.governments.issue_bonds.assert_called_with()
    model.governments.update_bond_rate.assert_called_with()
    model.governments.update_history.assert_called_with()


def test_bond_markets_matching(params):
    # Given
    model = EcoModel(params)
    model.banks = Mock()
    model.national_central_banks = Mock()

    # When
    model._bond_markets_matching()

    # Then
    model.banks.buy_bonds.assert_called_with()
    model.national_central_banks.buy_bonds.assert_called_with()


def test_goods_consumption(params):
    # Given
    model = EcoModel(params)
    model.households = Mock()
    model.governments = Mock()

    # When
    model._goods_consumption()

    # Then
    model.governments.pay_public_transfers.assert_called_with()
    model.households.calc_consumption.assert_called_with()
    model.households.consume.assert_called_with()


def test_profit_distribution_planning(params):
    # Given
    model = EcoModel(params)
    model.firms = Mock()
    model.banks = Mock()
    model.union_central_bank = Mock()
    model.national_central_banks = Mock()

    # When
    model._profit_distribution_planning()

    # Then
    model.firms.repay_loans.assert_called_with()
    model.firms.compute_profit_distribution.assert_called_with()
    model.firms.update_net_worth.assert_called_with()
    model.firms.update_production_history.assert_called_with()
    model.banks.repay_cash_advances.assert_called_with()
    model.banks.compute_profit_distribution.assert_called_with()
    model.banks.update_net_worth.assert_called_with()
    model.national_central_banks.transfer_profit.assert_called_with()
    model.union_central_bank.update_discount_rate.assert_called_with()
    model.national_central_banks.implement_discount_rate.assert_called_with()


def test_enter_exit(params):
    # Given
    model = EcoModel(params)
    model.households = Mock()
    model.firms = Mock()
    model.banks = Mock()
    model.governments = Mock()
    model.national_central_banks = Mock()

    # When
    model._enter_exit()

    # Then
    model.households.choose_portfolio_allocation.assert_called_with()
    model.households.invest_equity.assert_called_with()
    model.households.choose_deposit_bank.assert_called_with()
    model.households.make_deposits.assert_called_with()
    model.firms.exit.assert_called_with()
    model.banks.exit.assert_called_with()
    model.governments.issue_deposit_guarantee_bonds.assert_called_with()
    model.national_central_banks.buy_bonds.assert_called_with()
    model.governments.reimburse_deposits.assert_called_with()
