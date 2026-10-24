import pytest
from unittest.mock import Mock, MagicMock
from agentpy import AgentList, AgentDList
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
        "omega": 0.1,
        "initial_wage": 1.0,
        "initial_phi": 1.0,
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
        "initial_public_transfer": 0.4,
        "inflation_target": 0.005,
        "dmax": 0.03,
        "tax_min": 0.35,
        "tax_max": 0.45,
        "g_min": 0.4,
        "g_max": 0.6,
        "eta": 0.03,
        "initial_equity": 10.0,
        "sigma": 4,
    }


@pytest.fixture
def before_setup(monkeypatch, params):
    # Given
    monkeypatch.setattr(EcoModel, "_create_union", Mock())
    monkeypatch.setattr(EcoModel, "_create_households", Mock())
    monkeypatch.setattr(EcoModel, "_create_governments", Mock())
    monkeypatch.setattr(EcoModel, "_create_central_banks", Mock())
    model = EcoModel(params)
    return model


def test_setup_calls_4_sub_procedures(before_setup):
    # Given
    model = before_setup

    # When
    model.setup()

    # Then
    model._create_union.assert_called_once_with()
    model._create_households.assert_called_once_with()
    model._create_governments.assert_called_once_with()
    model._create_central_banks.assert_called_once_with()


def test_setup_creates_firms_as_empty_agent_dlist(before_setup):
    # Given
    model = before_setup

    # When
    model.setup()

    # Then
    assert isinstance(model.firms, AgentDList)


def test_setup_creates_banks_as_empty_agent_dlist(before_setup):
    # Given
    model = before_setup

    # When
    model.setup()

    # Then
    assert isinstance(model.banks, AgentDList)


FakeUnion = Mock()


@pytest.fixture
def before_union_creation(monkeypatch, params):
    # Given
    monkeypatch.setattr("model.model.MonetaryUnion", FakeUnion)
    model = EcoModel(params)
    return model


def test_create_union_creates_monetary_union(before_union_creation):
    # Given
    model = before_union_creation

    # When
    model._create_union()

    # Then
    FakeUnion.assert_called_once_with(model)
    assert model.union is FakeUnion.return_value


def test_create_union_creates_markets(before_union_creation):
    # Given
    model = before_union_creation

    # When
    model._create_union()

    # Then
    model.union.create_markets.assert_called_with()


def test_create_union_creates_countries(before_union_creation):
    # Given
    model = before_union_creation

    # When
    model._create_union()

    # Then
    model.union.create_countries.assert_called_with()


FakeHousehold = MagicMock()
FakeGovt = MagicMock()
FakeCBank = MagicMock()


@pytest.fixture
def before_agents_creation(monkeypatch, params):
    # Given
    monkeypatch.setattr("model.model.Household", FakeHousehold)
    monkeypatch.setattr("model.model.Government", FakeGovt)
    monkeypatch.setattr("model.model.CentralBank", FakeCBank)
    model = EcoModel(params)
    model.union = Mock()
    return model


def test_create_households_creates_sufficient_agent_number(before_agents_creation):
    # Given
    model = before_agents_creation
    h_num = model.p.household_number
    c_num = model.p.country_number

    # When
    model._create_households()

    # Then
    assert len(model.households) == h_num * c_num
    for household in model.households:
        assert household is FakeHousehold.return_value


def test_create_households_sets_new_agents_country_pos(before_agents_creation):
    # Given
    model = before_agents_creation
    model.p.household_number = 2
    model.p.country_number = 2
    expected = [0, 1, 0, 1]

    # When
    model._create_households()

    # Then
    assert model.households.country_pos == expected


def test_create_households_adds_agents_to_union(before_agents_creation):
    # Given
    model = before_agents_creation
    union = model.union

    # When
    model._create_households()

    # Then
    union.add_agents.assert_any_call(model.households)


def test_create_governments_creates_sufficient_agent_number(before_agents_creation):
    # Given
    model = before_agents_creation

    # When
    model._create_governments()

    # Then
    assert len(model.governments) == model.p.country_number
    for govt in model.governments:
        assert govt is FakeGovt.return_value


def test_create_governments_sets_new_agents_country_pos(before_agents_creation):
    # Given
    model = before_agents_creation
    expected = list(range(model.p.country_number))

    # When
    model._create_governments()

    # Then
    assert model.governments.country_pos == expected


def test_create_governments_adds_agents_to_union(before_agents_creation):
    # Given
    model = before_agents_creation
    union = model.union

    # When
    model._create_governments()

    # Then
    union.add_agents.assert_any_call(model.governments)


def test_create_central_banks_creates_sufficient_agent_number(before_agents_creation):
    # Given
    model = before_agents_creation

    # When
    model._create_central_banks()

    # Then
    assert len(model.national_cbs) == model.p.country_number
    assert model.union_cb is FakeCBank.return_value
    for cb in model.national_cbs:
        assert cb is FakeCBank.return_value


def test_create_central_banks_sets_national_cbs_country_pos(before_agents_creation):
    # Given
    model = before_agents_creation
    model.p.country_number = 3
    expected = [0, 1, 2]

    # When
    model._create_central_banks()

    # Then
    assert model.national_cbs.country_pos == expected


def test_create_central_banks_sets_new_agents_national_property(before_agents_creation):
    # Given
    model = before_agents_creation
    FakeCBank.side_effect = lambda *a, **kw: Mock()

    # When
    model._create_central_banks()

    # Then
    assert model.union_cb.national == False
    assert set(model.national_cbs.national) == {True}


def test_create_central_banks_adds_agents_to_union(before_agents_creation):
    # Given
    model = before_agents_creation
    union = model.union

    # When
    model._create_central_banks()

    # Then
    union.add_agents.assert_any_call([model.union_cb])
    union.add_agents.assert_any_call(model.national_cbs)


# ---------------------------------------------------
# STEP PROCESS
# ----------------------------------------------------


@pytest.fixture
def before_step(monkeypatch):
    # Given
    monkeypatch.setattr(EcoModel, "_clear_defaults_and_transactions", Mock())
    monkeypatch.setattr(EcoModel, "_production_and_rd_planning", Mock())
    monkeypatch.setattr(EcoModel, "_credit_markets_matching", Mock())
    monkeypatch.setattr(EcoModel, "_labor_markets_matching", Mock())
    monkeypatch.setattr(EcoModel, "_production_and_incomes_distribution", Mock())
    monkeypatch.setattr(EcoModel, "_tax_collection_and_public_expenditures", Mock())
    monkeypatch.setattr(EcoModel, "_bond_markets_matching", Mock())
    monkeypatch.setattr(EcoModel, "_goods_consumption", Mock())
    monkeypatch.setattr(EcoModel, "_profit_distribution_planning", Mock())
    monkeypatch.setattr(EcoModel, "_enter_exit", Mock())
    monkeypatch.setattr(EcoModel, "_update_union_state", Mock())


@pytest.mark.usefixtures("before_step")
def test_step_calls_union_evolution_procedures(params):
    # Given
    model = EcoModel(params)

    # When
    model.step()

    # Then
    model._clear_defaults_and_transactions.assert_called_with()
    model._update_union_state.assert_called_with()


@pytest.mark.usefixtures("before_step")
def test_step_calls_5_first_events_procedures(params):
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


@pytest.mark.usefixtures("before_step")
def test_step_calls_4_last_events_procedures(params):
    # Given
    model = EcoModel(params)

    # When
    model.step()

    # Then
    model._bond_markets_matching.assert_called_with()
    model._goods_consumption.assert_called_with()
    model._profit_distribution_planning.assert_called_with()
    model._enter_exit.assert_called_with()


def test_clear_defaults_and_transactions(params, make_dlist):
    # Given
    model = EcoModel(params)
    model.union = Mock()
    model.firms = make_dlist([Mock(defaulted=True), Mock(defaulted=False)])
    model.banks = make_dlist([Mock(defaulted=True), Mock(defaulted=False)])

    # When
    model._clear_defaults_and_transactions()

    # Then
    assert model.union.clear_transactions.called
    assert model.union.clear_defaults.called
    assert len(model.firms) == 1
    assert len(model.banks) == 1


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
    model.firms.calc_desired_rd.assert_called_with()


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
    model.households.update_labor_history.assert_called_with()


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
    model.firms.execute_rd.assert_called_with()
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
    model.governments.update_budget_history.assert_called_with()


def test_bond_markets_matching(params):
    # Given
    model = EcoModel(params)
    model.banks = Mock()
    model.national_cbs = Mock()

    # When
    model._bond_markets_matching()

    # Then
    model.banks.buy_bonds.assert_called_with()
    model.national_cbs.buy_bonds.assert_called_with()


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
    model.union_cb = Mock()
    model.national_cbs = Mock()

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
    model.national_cbs.transfer_profit.assert_called_with()
    model.union_cb.update_discount_rate.assert_called_with()
    model.national_cbs.implement_discount_rate.assert_called_with()


def test_enter_exit(params):
    # Given
    model = EcoModel(params)
    model.households = Mock()
    model.firms = Mock()
    model.banks = Mock()
    model.governments = Mock()
    model.national_cbs = Mock()

    # When
    model._enter_exit()

    # Then
    model.households.choose_portfolio_allocation.assert_called_with()
    model.households.invest_equity.assert_called_with()
    model.firms.exit.assert_called_with()
    model.banks.exit.assert_called_with()
    model.governments.issue_deposit_guarantee_bonds.assert_called_with()
    model.national_cbs.buy_bonds.assert_called_with()
    model.governments.reimburse_deposits.assert_called_with()


def test_update_union_state(params):
    # Given
    model = EcoModel(params)
    model.union = Mock()

    # When
    model._update_union_state()

    # Then
    model.union.update_state.assert_called_with()


# ---------------------------------------------------
# UPDATE PROCESS
# ----------------------------------------------------


@pytest.fixture
def before_update(params):
    # Given
    model = EcoModel(params)
    model.households = Mock()
    model.firms = Mock()
    model.banks = Mock()
    model.governments = Mock()
    model.national_cbs = Mock()
    model.union_cb = Mock()
    model.union = Mock()
    return model


def test_update_records_households_account(before_update):
    # Given
    model = before_update

    # When
    model.update()

    # Then
    model.households.record_account.assert_called_with()


def test_update_records_firms_account(before_update):
    # Given
    model = before_update

    # When
    model.update()

    # Then
    model.firms.record_account.assert_called_with()


def test_update_records_banks_account(before_update):
    # Given
    model = before_update

    # When
    model.update()

    # Then
    model.banks.record_account.assert_called_with()


def test_update_records_governments_account(before_update):
    # Given
    model = before_update

    # When
    model.update()

    # Then
    model.governments.record_account.assert_called_with()


def test_update_records_national_cbs_account(before_update):
    # Given
    model = before_update

    # When
    model.update()

    # Then
    model.national_cbs.record_account.assert_called_with()


def test_update_records_union_cb_account(before_update):
    # Given
    model = before_update

    # When
    model.update()

    # Then
    model.union_cb.record_account.assert_called_with()
