import math
import pytest
from unittest.mock import Mock
from model.agents.household import Household

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_agent():
    # Given
    from model.extensions import EcoAgent

    # Then
    assert issubclass(Household, EcoAgent)


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_wage = 5.0
    model.nprandom = Mock()
    model.random = Mock()
    return model


@pytest.fixture
def household(model):
    # Given
    return Household(model)


def test_initializes_labor_supply(household):
    # Then
    assert household.labor_supply == 1.0


def test_initializes_prev_labor_sold(household):
    # Then
    assert household.prev_labor_sold == 0.0


def test_initializes_preference_randomly(household, model):
    # Given
    random = model.nprandom
    random.uniform.return_value = 0.4

    # When
    household = Household(model)

    # Then
    random.uniform.assert_called_with(0, math.radians(360))
    assert household.preference == 0.4


def test_initializes_reservation_wage(household, model):
    # Then
    assert household.reservation_wage == model.p.initial_wage


def test_initializes_expected_consumption(household):
    # Then
    assert household.expected_consumption == 0


def test_initializes_desired_consumption(household):
    # Then
    assert household.desired_consumption == 0


def test_initializes_desired_equity(household):
    # Then
    assert household.desired_equity == 0


def test_initializes_desired_deposits(household):
    # Then
    assert household.desired_deposits == 0


def test_initializes_desired_investment_sector(household):
    # Then
    assert household.desired_investment_sector is None


def test_initializes_net_worth(household):
    # Then
    assert household.net_worth == 0


def test_initializes_incomes(household):
    # Then
    assert household.income == 0
    assert household.disposable_income == 0


# ----------------------------------------------------
# JOB SEARCH
# ----------------------------------------------------


@pytest.fixture
def account(household):
    # Given
    account = {}
    household.account = account
    return account


@pytest.fixture
def worker_role(household):
    # Given
    role = Mock(labor_supply=1.0, labor_sold=0.0)
    household.roles["worker"] = role
    return role


@pytest.fixture
def unemployed(household, worker_role):
    # Given
    household.p.psi = 6
    household.labor_supply = 1.0
    household.reservation_wage = 10
    worker_role.find_employers.return_value = []
    return household


def test_search_jobs_with_limited_size(unemployed, worker_role):
    # Given
    household = unemployed

    # When
    household.search_jobs()

    # Then
    worker_role.find_employers.assert_called_with(household.p.psi)


def test_search_jobs_with_highest_wage(unemployed, worker_role):
    # Given
    household = unemployed
    employer1 = Mock(wage=15, labor_demand=1.0)
    employer2 = Mock(wage=20, labor_demand=1.0)
    worker_role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    worker_role.accept_job.assert_called_with(employer2, pytest.approx(1.0))


def test_search_jobs_with_sufficient_wage_offered(unemployed, worker_role):
    # Given
    household = unemployed
    employer1 = Mock(wage=8, labor_demand=1.0)
    employer2 = Mock(wage=9, labor_demand=1.0)
    worker_role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    worker_role.accept_job.assert_not_called()


def test_search_jobs_and_split_labor_between_employers(unemployed, worker_role):
    # Given
    household = unemployed
    employer1 = Mock(wage=20, labor_demand=0.4)
    employer2 = Mock(wage=15, labor_demand=0.6)
    household = unemployed
    worker_role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    worker_role.accept_job.assert_any_call(employer1, pytest.approx(0.4))
    worker_role.accept_job.assert_any_call(employer2, pytest.approx(0.6))


def test_search_jobs_while_labor_supply_is_remaining(unemployed, worker_role):
    # Given
    household = unemployed
    employer1 = Mock(wage=25, labor_demand=0.7)
    employer2 = Mock(wage=20, labor_demand=0.7)
    worker_role.find_employers.return_value = [employer1, employer2]
    worker_role.labor_supply = 0.5

    # When
    household.search_jobs()

    # Then
    worker_role.accept_job.assert_any_call(employer1, pytest.approx(0.5))


# ---------------------------------------------------
# WAGE REVISION
# ----------------------------------------------------


def test_calc_revision_probability(household, worker_role):
    # Given
    household.p.upsilon = 1.0
    worker_role.get_unemployment.return_value = 0.1

    # When
    result = household._calc_revision_probability()

    # Then
    assert result == math.exp(-1.0 * 0.1)


@pytest.fixture
def fully_employed_before(household):
    # Given
    household.model.nprandom = Mock()
    household.p.delta = 0.9
    household.prev_labor_sold = 1.0
    household.reservation_wage = 10.0
    household._calc_revision_probability = Mock()
    household._calc_revision_probability.return_value = 0
    return household


def test_increases_reserv_wage_when_fully_employed(fully_employed_before):
    # Given
    household = fully_employed_before
    random = household.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    random.uniform.assert_called_with(0, household.p.delta)
    assert household.reservation_wage > 10.0


def test_increases_reserv_wage_with_upward_revision_prob(fully_employed_before):
    # Given
    household = fully_employed_before
    household._calc_revision_probability.return_value = 0.6
    random = household.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    random.choice.assert_called_with([0, 1], p=[1 - 0.6, 0.6])


def test_can_choose_to_not_increases_reserv_wage(fully_employed_before):
    # Given
    household = fully_employed_before
    random = household.model.nprandom
    random.choice.return_value = 0
    random.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    random.uniform.assert_not_called()
    assert household.reservation_wage == 10.0


@pytest.fixture
def part_employed_before(household):
    # Given
    household.model.nprandom = Mock()
    household.p.delta = 0.9
    household.prev_labor_sold = 0.5
    household.reservation_wage = 10.0
    household._calc_revision_probability = Mock()
    household._calc_revision_probability.return_value = 0
    return household


def test_decreases_reserv_wage_when_not_fully_employed(part_employed_before):
    # Given
    household = part_employed_before
    random = household.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    random.uniform.assert_called_with(0, household.p.delta)
    assert household.reservation_wage < 10.0


def test_decreases_reserv_wage_with_downward_revision_prob(part_employed_before):
    # Given
    household = part_employed_before
    household._calc_revision_probability.return_value = 0.6
    random = household.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 1 - 0.6])


def test_can_choose_to_not_decreases_reserv_wage(part_employed_before):
    # Given
    household = part_employed_before
    random = household.model.nprandom
    random.choice.return_value = 0
    random.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    random.uniform.assert_not_called()
    assert household.reservation_wage == 10.0


# ---------------------------------------------------
# INCOME COMPUTATION AND TAX PAYMENT
# ----------------------------------------------------


@pytest.fixture
def citizen_role(household):
    # Given
    role = Mock()
    household.roles["citizen"] = role
    return role


@pytest.fixture
def household_before_tax(household, citizen_role):
    # Given
    citizen_role.get_tax_rate.return_value = 0.2
    return household


def test_calc_income(household_before_tax, account):
    # Given
    household = household_before_tax
    account["wages"] = 110
    account["dep_interests"] = 20
    account["dividends"] = 30

    # When
    income = household._calc_income()

    # Then
    assert income == 160


def test_calc_disposable_income(household_before_tax, account):
    # Given
    household = household_before_tax
    household.income = 200
    account["public_transfers"] = 50

    # When
    disposable_income = household._calc_disposable_income()

    # Then
    assert disposable_income == 210


def test_pay_taxes_transfers_cash(household_before_tax, citizen_role):
    # Given
    household = household_before_tax
    household._calc_income = Mock(return_value=100)
    household._calc_disposable_income = Mock(return_value=110)

    # When
    household.pay_taxes()

    # Then
    citizen_role.pay_taxes.assert_called_with(20)


def test_pay_taxes_updates_indicators(household_before_tax):
    # Given
    household = household_before_tax
    household._calc_income = Mock(return_value=100)
    household._calc_disposable_income = Mock(return_value=110)

    # When
    household.pay_taxes()

    # Then
    assert household.disposable_income == 110
    assert household.income == 100


# ---------------------------------------------------
# CONSUMPTION
# ----------------------------------------------------


def test_calc_consumption_updates_choice(household, account):
    # Given
    household.p.cy = 0.8
    household.p.cd = 0.1
    household.disposable_income = 1000
    account["deposits"] = 500

    # When
    consumption = household.calc_consumption()

    # Then
    assert consumption == 850
    assert household.desired_consumption == 850


@pytest.fixture
def any_consumer_role():
    # Given
    role = Mock()
    role.get_average_price.return_value = 1
    role.find_suppliers.return_value = []
    return role


@pytest.fixture
def household_before_any_cons(household, account):
    # Given
    household.p.psi = 1
    account["cash"] = 1000
    return household


def test_calc_supplier_score_with_salop_formula(household):
    # Given
    household.p.beta = 1
    household.preference = 0
    supplier = Mock(variety=0.5, price=10)

    # When
    score = household._calc_supplier_score(supplier, average_price=20)

    # Then
    expected_distance = math.sin(0.5 / 2)
    assert score == (1 / expected_distance) * (20 / 10)


def test_rank_suppliers_using_supplier_score(household):
    # Given
    suppliers = [Mock(price=i, variety=1) for i in range(1, 3)]
    method = lambda supplier, average_price: average_price / supplier.price
    household._calc_supplier_score = method

    # When
    ranked = household._rank_suppliers(suppliers, average_price=10)

    # Then
    assert ranked[0].price == 1
    assert ranked[1].price == 2


def test_consume_good_with_found_suppliers(
    household_before_any_cons,
    any_consumer_role,
):
    # Given
    found = [Mock(price=5, inventories=10) for _ in range(5)]
    household = household_before_any_cons
    household.p.psi = 5
    household._rank_suppliers = Mock(return_value=found)
    any_consumer_role.find_suppliers.return_value = found
    any_consumer_role.get_average_price.return_value = 20

    # When
    household._consume_good(any_consumer_role, 100)

    # Then
    any_consumer_role.find_suppliers.assert_called_with(5)
    household._rank_suppliers.assert_any_call(found, average_price=20)


def test_consume_good_with_ranked_suppliers(
    household_before_any_cons, any_consumer_role
):
    # Given
    ranked = [Mock(price=5, inventories=10) for _ in range(2)]
    household = household_before_any_cons
    household.p.psi = 1
    household._rank_suppliers = Mock(return_value=ranked)

    # When
    household._consume_good(any_consumer_role, 100)

    # Then
    any_consumer_role.buy_goods.assert_any_call(ranked[0], 10)
    any_consumer_role.buy_goods.assert_any_call(ranked[1], 10)
    assert any_consumer_role.buy_goods.call_count == 2


def test_consume_good_with_desired_consumption(
    household_before_any_cons,
    any_consumer_role,
):
    # Given
    ranked = [Mock(price=5, inventories=10) for _ in range(2)]
    household = household_before_any_cons
    household.p.psi = 1
    household._rank_suppliers = Mock(return_value=ranked)

    # When
    household._consume_good(any_consumer_role, 50)

    # Then
    any_consumer_role.buy_goods.assert_any_call(ranked[0], 10)
    assert any_consumer_role.buy_goods.call_count == 1


def test_consume_good_with_supply_constraints(
    household_before_any_cons,
    any_consumer_role,
):
    # Given
    ranked = [Mock(price=5, inventories=5) for _ in range(2)]
    household = household_before_any_cons
    household.p.psi = 1
    household._rank_suppliers = Mock(return_value=ranked)

    # When
    household._consume_good(any_consumer_role, 100)

    # Then
    any_consumer_role.buy_goods.assert_any_call(ranked[0], 5)
    any_consumer_role.buy_goods.assert_any_call(ranked[1], 5)
    assert any_consumer_role.buy_goods.call_count == 2


def test_consume_good_with_monetary_constraints(
    household_before_any_cons,
    any_consumer_role,
):
    # Given
    ranked = [Mock(price=5, inventories=10) for _ in range(2)]
    household = household_before_any_cons
    household.account["cash"] = 50
    household._rank_suppliers = Mock(return_value=ranked)

    # When
    household._consume_good(any_consumer_role, 100)

    # Then
    any_consumer_role.buy_goods.assert_any_call(ranked[0], 10)
    assert any_consumer_role.buy_goods.call_count == 1


@pytest.fixture
def trad_consumer_role(household):
    # Given
    role = Mock()
    household.roles["trad_consumer"] = role
    return role


@pytest.fixture
def non_trad_consumer_role(household):
    # Given
    role = Mock()
    household.roles["non_trad_consumer"] = role
    return role


@pytest.fixture
def household_before_all_cons(
    household,
    account,
    trad_consumer_role,
    non_trad_consumer_role,
):
    # Given
    _ = trad_consumer_role
    _ = non_trad_consumer_role
    household.p.cT = 0.6
    household.desired_consumption = 100
    household._withdraw_deposits = Mock()
    household._consume_good = Mock()
    account["cash"] = 100
    return household


def test_consume_each_good_type(
    household_before_all_cons,
    trad_consumer_role,
    non_trad_consumer_role,
):
    # Given
    household = household_before_all_cons

    # When
    household.consume()

    # Then
    household._consume_good.assert_any_call(trad_consumer_role, 60.0)
    household._consume_good.assert_any_call(non_trad_consumer_role, 40.0)


def test_consume_randomizes_entry_order(household_before_all_cons):
    # Given
    entry_order = [("trad_consumer", 0.6), ("non_trad_consumer", 0.4)]
    household = household_before_all_cons
    random = household.model.random

    # When
    household.consume()

    # Then
    random.shuffle.assert_called_with(entry_order)


def test_consume_withdraws_needed_deposits(household_before_all_cons):
    # Given
    household = household_before_all_cons
    household.account["cash"] = 40

    # When
    household.consume()

    # Then
    household._withdraw_deposits.assert_called_with(60)


# ---------------------------------------------------
# PORTFOLIO ALLOCATION
# ----------------------------------------------------


@pytest.fixture
def depositor_role(household):
    # Given
    role = Mock()
    household.roles["depositor"] = role
    return role


@pytest.fixture
def household_before_allocation(household, account, citizen_role):
    # Given
    _ = citizen_role
    account["cash"] = 1000
    return household


def test_calc_net_worth(household_before_allocation):
    # Given
    household = household_before_allocation
    household.account["deposits"] = 200
    household.account["equities"] = 300
    household.account["cash"] = 500

    # When
    household._calc_net_worth()

    # Then
    assert household.net_worth == 1000


def test_calc_expected_net_worth(household_before_allocation):
    # Given
    household = household_before_allocation
    household.net_worth = 1000
    household.disposable_income = 300
    household.expected_consumption = 200

    # When
    expected_worth = household._calc_expected_net_worth()

    # Then
    assert expected_worth == 1100


def test_calc_liquidity_pref_with_deposit_bank_rate(
    household_before_allocation,
    citizen_role,
    depositor_role,
):
    # Given
    household = household_before_allocation
    household.account["dividends"] = 10
    household.account["equities"] = 100
    household.p.lambda_ = 0.6
    citizen_role.get_prob_failure.return_value = 0.10
    depositor_role.get_deposit_rate.return_value = 0.05

    # When
    household._calc_liquidity_preference()

    # Then
    depositor_role.get_deposit_rate.assert_called_with()


def test_calc_liquidity_pref_when_equity_is_more_profitable(
    household_before_allocation,
    citizen_role,
    depositor_role,
):
    # Given
    household = household_before_allocation
    household.account["dividends"] = 10
    household.account["equities"] = 100
    household.p.lambda_ = 0.6
    citizen_role.get_prob_failure.return_value = 0.10
    depositor_role.get_deposit_rate.return_value = 0.05
    expected = 0.6 * math.exp(((10 * (1 - 0.10)) / 100) - 0.05)

    # When
    lp = household._calc_liquidity_preference()

    # Then
    assert lp == pytest.approx(expected)


def test_calc_liquidity_pref_when_equity_is_less_profitable(
    household_before_allocation,
    citizen_role,
    depositor_role,
):
    # Given
    household = household_before_allocation
    household.account["dividends"] = 2
    household.account["equities"] = 100
    household.p.lambda_ = 0.7
    citizen_role.get_prob_failure.return_value = 0.10
    depositor_role.get_deposit_rate.return_value = 0.05

    # When
    lp = household._calc_liquidity_preference()

    # Then
    assert lp == 0.7


def test_calc_liquidity_preference_when_no_equity(
    household_before_allocation,
    citizen_role,
    depositor_role,
):
    # Given
    household = household_before_allocation
    household.account["dividends"] = 0
    household.account["equities"] = 0
    household.p.lambda_ = 0.8
    citizen_role.get_prob_failure.return_value = 0.10
    depositor_role.get_deposit_rate.return_value = 0.05

    # When
    lp = household._calc_liquidity_preference()

    # Then
    assert lp == 0.8


def test_choose_portfolio_calc_net_worth(household_before_allocation):
    # Given
    household = household_before_allocation
    household.account["equities"] = 80
    household._calc_liquidity_preference = Mock(return_value=0.80)
    household._calc_expected_net_worth = Mock(return_value=100)
    household._calc_net_worth = Mock()

    # When
    household.choose_portfolio()

    # Then
    household._calc_net_worth.assert_called_once_with()


def test_choose_portfolio_updates_desired_assets(household_before_allocation):
    # Given
    household = household_before_allocation
    household.account["equities"] = 20
    household._calc_liquidity_preference = Mock(return_value=0.40)
    household._calc_expected_net_worth = Mock(return_value=100)
    household._calc_net_worth = Mock()

    # When
    household.choose_portfolio()

    # Then
    assert household.desired_equity == 60
    assert household.desired_deposits == 60


def test_choose_portfolio_preserves_existing_equity(household_before_allocation):
    # Given
    household = household_before_allocation
    household.account["equities"] = 80
    household._calc_liquidity_preference = Mock(return_value=0.80)
    household._calc_expected_net_worth = Mock(return_value=100)
    household._calc_net_worth = Mock()

    # When
    household.choose_portfolio()

    # Then
    assert household.desired_equity == 80


@pytest.mark.parametrize("cash, expected", [(0, 0), (50, 50), (100, 80)])
def test_choose_portfolio_exposes_investment(
    household_before_allocation,
    citizen_role,
    cash,
    expected,
):
    # Given
    household = household_before_allocation
    household.account["equities"] = 80
    household.account["cash"] = cash
    household._calc_liquidity_preference = Mock(return_value=0.80)
    household._calc_expected_net_worth = Mock(return_value=100)
    household._calc_net_worth = Mock()

    # When
    household.choose_portfolio()

    # Then
    assert citizen_role.desired_investment == expected


# ---------------------------------------------------
# FIRM AND BANK CREATION
# ----------------------------------------------------


@pytest.fixture
def before_investment(household_before_allocation):
    # Given
    household = household_before_allocation
    household._choose_investment_sector = Mock()
    household._calc_initial_equity = Mock()
    household._collect_equity_shares = Mock(return_value=None)
    household._create_company = Mock()
    household._fund_company = Mock()
    household._choose_deposit_bank = Mock()
    household._make_deposits = Mock()
    return household


def test_invest_equity_does_nothing_if_no_desired_equity(before_investment):
    # Given
    household = before_investment
    household.desired_equity = 0

    # When
    household.invest_equity()

    # Then
    household._choose_investment_sector.assert_not_called()
    household._calc_initial_equity.assert_not_called()
    household._collect_equity_shares.assert_not_called()
    household._create_company.assert_not_called()
    household._fund_company.assert_not_called()


def test_invest_equity_chooses_investment_sector(before_investment):
    # Given
    household = before_investment
    household.desired_equity = 100

    # When
    household.invest_equity()

    # Then
    household._choose_investment_sector.assert_called_once_with()


def test_invest_equity_calcs_initial_equity_with_sector(before_investment):
    # Given
    household = before_investment
    household.desired_equity = 100
    household._choose_investment_sector.return_value = "ANY"

    # When
    household.invest_equity()

    # Then
    household._calc_initial_equity.assert_called_once_with("ANY")


def test_invest_equity_collects_equity_shares_with_target(before_investment):
    # Given
    household = before_investment
    household.desired_equity = 100
    household._calc_initial_equity.return_value = 250

    # When
    household.invest_equity()

    # Then
    household._collect_equity_shares.assert_called_once_with(250)


def test_invest_equity_creates_company_with_sector_and_size(before_investment):
    # Given
    shares = [dict(amount=100) for _ in range(2)]
    household = before_investment
    household.desired_equity = 100
    household._collect_equity_shares.return_value = shares
    household._choose_investment_sector.return_value = "ANY"

    # When
    household.invest_equity()

    # Then
    household._create_company.assert_called_once_with("ANY", 200)


def test_invest_equity_stop_creation_process_if_no_shares(before_investment):
    # Given
    household = before_investment
    household.desired_equity = 100
    household._collect_equity_shares.return_value = None
    household._choose_investment_sector.return_value = "ANY"

    # When
    household.invest_equity()

    # Then
    household._create_company.assert_not_called()
    household._fund_company.assert_not_called()


def test_invest_equity_funds_company_with_new_agent_and_shares(before_investment):
    # Given
    shares = [dict(amount=100) for _ in range(2)]
    household = before_investment
    household.desired_equity = 100
    household._collect_equity_shares.return_value = shares
    household._choose_investment_sector.return_value = "ANY"
    household._create_company.return_value = 5

    # When
    household.invest_equity()

    # Then
    household._fund_company.assert_called_once_with(5, shares)


def test_invest_equity_make_deposits_with_residuals(before_investment):
    # Given
    bank_id = 5
    household = before_investment
    household._choose_deposit_bank.return_value = bank_id

    # When
    household.invest_equity()

    # Then
    household._choose_deposit_bank.assert_called_once_with()
    household._make_deposits.assert_called_once_with(5)


def test_invest_equity_doesnt_make_deposits_if_no_banks(before_investment):
    # Given
    household = before_investment
    household._choose_deposit_bank.return_value = None

    # When
    household.invest_equity()

    # Then
    household._make_deposits.assert_not_called()


@pytest.fixture
def household_after_allocation(household_before_allocation):
    # Given
    household = household_before_allocation
    household.model.nprandom = Mock()
    return household


@pytest.mark.parametrize("ratio1, ratio2", [(0.2, 0.5), (0.5, 0.2)])
def test_choose_investment_sector_returns_bank_sector(
    household_after_allocation,
    citizen_role,
    ratio1,
    ratio2,
):
    # Given
    household = household_after_allocation
    household.p.cT = 0.6
    household.p.eta = 0.3
    citizen_role.get_bank_number_ratio.return_value = ratio1
    citizen_role.get_bank_equity_ratio.return_value = ratio2

    # When
    sector = household._choose_investment_sector()

    # Then
    assert sector == "B"


def test_choose_investment_sector_returns_random_firm_sector(
    household_after_allocation,
    citizen_role,
):
    # Given
    household = household_after_allocation
    household.p.cT = 0.6
    household.p.eta = 0.3
    citizen_role.get_bank_number_ratio.return_value = 0.6
    citizen_role.get_bank_equity_ratio.return_value = 0.6
    random = household.model.nprandom

    # When
    sector = household._choose_investment_sector()

    # Then
    random.choice.assert_called_with(["FNT", "FT"], p=[0.4, 0.6])
    assert sector == random.choice.return_value


@pytest.mark.parametrize("ratio", [0.2, 0.5, 0.6])
def test_choose_investment_sector_registers_desired_sector(
    household_after_allocation,
    citizen_role,
    ratio,
):
    # Given
    household = household_after_allocation
    household.p.cT = 0.6
    household.p.eta = 0.3
    citizen_role.get_bank_number_ratio.return_value = ratio
    citizen_role.get_bank_equity_ratio.return_value = ratio

    # When
    sector = household._choose_investment_sector()

    # Then
    assert household.desired_investment_sector == sector


def test_calc_initial_equity_chooses_equity_between_current_range(
    household_after_allocation,
    citizen_role,
):
    # Given
    household = household_after_allocation
    household.p.sigma = 1.0
    random = household.model.nprandom
    citizen_role.get_equity_range.return_value = (100, 500)

    # When
    equity = household._calc_initial_equity("ANY")

    # Then
    citizen_role.get_equity_range.assert_called_with("ANY")
    random.uniform.assert_called_once_with(100, 500)
    assert equity == random.uniform.return_value


def test_calc_initial_equity_returns_initial_equity_if_no_current_range(
    household_after_allocation,
    citizen_role,
):
    # Given
    household = household_after_allocation
    household.p.sigma = 1.0
    household.p.initial_equity = 1000
    random = household.model.nprandom
    citizen_role.get_equity_range.return_value = None

    # When
    equity = household._calc_initial_equity("ANY")

    # Then
    random.uniform.assert_not_called()
    assert equity == household.p.initial_equity


def test_calc_initial_equity_includes_median_firm_size_for_bank_sector(
    household_after_allocation,
    citizen_role,
):
    # Given
    household = household_after_allocation
    household.p.sigma = 0.5
    random = household.model.nprandom
    citizen_role.get_median_firm_size.return_value = 500
    citizen_role.get_equity_range.return_value = (100, 500)

    # When
    equity = household._calc_initial_equity("B")

    # Then
    citizen_role.get_median_firm_size.assert_called_once_with()
    random.uniform.assert_called_once_with(250, 500)
    assert equity == random.uniform.return_value


def test_calc_initial_equity_uses_median_firm_size_if_no_bank_sector(
    household_after_allocation,
    citizen_role,
):
    # Given
    household = household_after_allocation
    household.p.sigma = 0.5
    household.p.initial_equity = 1000
    random = household.model.nprandom
    citizen_role.get_median_firm_size.return_value = 500
    citizen_role.get_equity_range.return_value = None

    # When
    equity = household._calc_initial_equity("B")

    # Then
    citizen_role.get_median_firm_size.assert_called_once_with()
    random.uniform.assert_called_once_with(250, 1000)
    assert equity == random.uniform.return_value


@pytest.fixture
def investors(citizen_role):
    # Given
    investors = [Mock(desired_investment=10, company_number=i) for i in range(2)]
    citizen_role.desired_investment = 10
    citizen_role.find_investors.return_value = investors
    return investors


@pytest.fixture
def household_before_invest(household_after_allocation, citizen_role, investors):
    # Given
    _ = investors
    citizen_role.get_average_wage.return_value = 15.0
    household = household_after_allocation
    household.p.omega = 0.1
    household.p.psi = 5
    return household


def test_collect_equity_shares_builds_and_returns_shares(
    household_before_invest,
    citizen_role,
    investors,
):
    # Given
    household = household_before_invest
    founders = [citizen_role] + investors

    # When
    result = household._collect_equity_shares(30)

    # Then
    assert result == [{"citizen": founder, "amount": 10} for founder in founders]


def test_collect_equity_shares_with_an_minimum_equity_target(
    household_before_invest,
    citizen_role,
    investors,
):
    # Given
    household = household_before_invest
    founders = [citizen_role, investors[0]]

    # When
    result = household._collect_equity_shares(15.0)

    # Then
    assert result == [{"citizen": founder, "amount": 10} for founder in founders]


def test_collect_equity_shares_returns_none_if_low_funds(household_before_invest):
    # Given
    household = household_before_invest

    # When
    result = household._collect_equity_shares(100.0)

    # Then
    assert result is None


def test_collect_equity_shares_with_minimum_level_of_equity(
    household_before_invest,
    citizen_role,
    investors,
):
    # Given
    household = household_before_invest
    ineligible, eligible = investors
    ineligible.desired_investment = 0.5
    founders = [citizen_role, eligible]

    # When
    result = household._collect_equity_shares(20)

    # Then
    assert result == [{"citizen": founder, "amount": 10} for founder in founders]


def test_collect_equity_shares_with_maximum_company_number(
    household_before_invest,
    citizen_role,
    investors,
):
    # Given
    household = household_before_invest
    ineligible, eligible = investors
    ineligible.company_number = 6
    founders = [citizen_role, eligible]

    # When
    result = household._collect_equity_shares(20)

    # Then
    assert result == [{"citizen": founder, "amount": 10} for founder in founders]


FakeFirm = Mock()


@pytest.fixture
def before_firm_creation(monkeypatch, household_after_allocation):
    # Given
    monkeypatch.setattr("model.agents.household.Firm", FakeFirm)
    equity_size = 100
    household = household_after_allocation
    household.model.union = Mock()
    household.model.firms = []
    household._resize_new_firm = Mock()
    return household, equity_size


def test_create_company_creates_firm_with_model(before_firm_creation):
    # Given
    household, equity_size = before_firm_creation

    # When
    household._create_company("ANY", equity_size)

    # Then
    FakeFirm.assert_called_with(household.model)


def test_create_company_sets_new_firm_country_pos(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, equity_size = before_firm_creation
    household.country_pos = 5

    # When
    household._create_company("ANY", equity_size)

    # Then
    assert firm.country_pos == 5


@pytest.mark.parametrize("sector, tradable", [("FT", True), ("FNT", False)])
def test_create_company_sets_new_firm_tradable(before_firm_creation, sector, tradable):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, equity_size = before_firm_creation

    # When
    household._create_company(sector, equity_size)

    # Then
    assert firm.tradable == tradable


def test_create_company_resizes_new_firm(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, equity_size = before_firm_creation

    # When
    household._create_company("ANY", equity_size)

    # Then
    household._resize_new_firm.assert_called_with(firm, "ANY", equity_size)


def test_create_company_adds_firm_into_union(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, equity_size = before_firm_creation
    union = household.model.union

    # When
    household._create_company("ANY", equity_size)

    # Then
    union.add_agents.assert_called_once_with([firm])


def test_create_company_appends_to_model_firms(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, equity_size = before_firm_creation

    # When
    household._create_company("ANY", equity_size)

    # Then
    assert firm in household.model.firms


@pytest.fixture
def before_firm_resize(household_after_allocation, citizen_role):
    # Given
    firm = Mock()
    firm.roles = {"employer": Mock(), "producer": Mock()}
    household = household_after_allocation
    household.p.initial_wage = 1.0
    household.p.initial_phi = 1.0
    citizen_role.get_phi_range.return_value = [0, 0]
    citizen_role.get_price_range.return_value = [0, 0]
    citizen_role.get_sales_range.return_value = [0, 0]
    citizen_role.get_wage_range.return_value = [0, 0]
    random = household.model.nprandom
    random.uniform = lambda a, b: (a + b) / 2
    return household, citizen_role, firm


def test_resize_new_firm_sets_variety_randomly(before_firm_resize):
    # Given
    max_variety = math.radians(360)
    household, citizen_role, firm = before_firm_resize
    citizen_role.get_sector_size.return_value = 0
    producer_role = firm.roles["producer"]

    # When
    household._resize_new_firm(firm, "ANY", 100)

    # Then
    assert producer_role.variety == pytest.approx(max_variety / 2)


def test_resize_new_firm_sets_phi_from_range(before_firm_resize):
    # Given
    household, citizen_role, firm = before_firm_resize
    citizen_role.get_phi_range.return_value = (1.0, 2.0)
    citizen_role.get_sector_size.return_value = 2
    producer_role = firm.roles["producer"]

    # When
    household._resize_new_firm(firm, "ANY", 100)

    # Then
    assert producer_role.phi == pytest.approx(1.5)


def test_resize_new_firm_sets_phi_from_params(before_firm_resize):
    # Given
    household, citizen_role, firm = before_firm_resize
    household.p.initial_phi = 0.5
    producer_role = firm.roles["producer"]
    citizen_role.get_sector_size.return_value = 1

    # When
    household._resize_new_firm(firm, "ANY", 100)

    # Then
    assert producer_role.phi == pytest.approx(0.5)


def test_resize_new_firm_sets_price_from_range(before_firm_resize):
    # Given
    household, citizen_role, firm = before_firm_resize
    citizen_role.get_price_range.return_value = (5.0, 15.0)
    citizen_role.get_sector_size.return_value = 2
    producer_role = firm.roles["producer"]

    # When
    household._resize_new_firm(firm, "ANY", 100)

    # Then
    assert producer_role.price == pytest.approx(10.0)


def test_resize_new_firm_sets_price_from_params(before_firm_resize):
    # Given
    household, citizen_role, firm = before_firm_resize
    household.p.initial_wage = 2.0
    household.p.initial_phi = 0.5
    producer_role = firm.roles["producer"]
    citizen_role.get_sector_size.return_value = 1

    # When
    household._resize_new_firm(firm, "ANY", 100)

    # Then
    assert producer_role.price == pytest.approx(2.0 / 0.5)


def test_resize_new_firm_sets_sales_from_range(before_firm_resize):
    # Given
    household, citizen_role, firm = before_firm_resize
    citizen_role.get_sales_range.return_value = (50.0, 100.0)
    citizen_role.get_sector_size.return_value = 2

    # When
    household._resize_new_firm(firm, "ANY", 100)

    # Then
    assert firm.expected_sales == pytest.approx(75.0)


def test_resize_new_firm_sets_sales_from_params(before_firm_resize):
    # Given
    household, citizen_role, firm = before_firm_resize
    household.p.initial_wage = 2.0
    household.p.initial_phi = 0.5
    citizen_role.get_sector_size.return_value = 1

    # When
    household._resize_new_firm(firm, "ANY", 100)

    # Then
    assert firm.expected_sales == pytest.approx(0.5 * 100 / 2.0)


def test_resize_new_firm_sets_wage_from_range(before_firm_resize):
    # Given
    household, citizen_role, firm = before_firm_resize
    citizen_role.get_wage_range.return_value = (2.0, 4.0)
    citizen_role.get_sector_size.return_value = 2
    employer_role = firm.roles["employer"]

    # When
    household._resize_new_firm(firm, "ANY", 100)

    # Then
    assert employer_role.wage == pytest.approx(3.0)


def test_resize_new_firm_sets_wage_from_params(before_firm_resize):
    # Given
    household, citizen_role, firm = before_firm_resize
    household.p.initial_wage = 2.0
    employer_role = firm.roles["employer"]
    citizen_role.get_sector_size.return_value = 1

    # When
    household._resize_new_firm(firm, "ANY", 100)

    # Then
    assert employer_role.wage == pytest.approx(2.0)


FakeBank = Mock()


@pytest.fixture
def before_bank_creation(monkeypatch, household_after_allocation):
    # Given
    monkeypatch.setattr("model.agents.household.Bank", FakeBank)
    equity_size = 150
    household = household_after_allocation
    household.model.union = Mock()
    household.model.banks = []
    return household, equity_size


def test_create_company_creates_bank_with_model(before_bank_creation):
    # Given
    household, equity_size = before_bank_creation

    # When
    household._create_company("B", equity_size)

    # Then
    FakeBank.assert_called_with(household.model)


def test_create_company_sets_new_bank_country_pos(before_bank_creation):
    # Given
    bank = Mock()
    FakeBank.return_value = bank
    household, equity_size = before_bank_creation
    household.country_pos = 4

    # When
    household._create_company("B", equity_size)

    # Then
    assert bank.country_pos == 4


def test_create_company_adds_bank_into_union(before_bank_creation):
    # Given
    bank = Mock()
    FakeBank.return_value = bank
    household, equity_size = before_bank_creation
    union = household.model.union

    # When
    household._create_company("B", equity_size)

    # Then
    union.add_agents.assert_called_once_with([bank])


def test_create_company_appends_to_model_banks(before_bank_creation):
    # Given
    bank = Mock()
    FakeBank.return_value = bank
    household, equity_size = before_bank_creation

    # When
    household._create_company("B", equity_size)

    # Then
    assert bank in household.model.banks


def test_fund_company_with_each_share(household_after_allocation):
    # Given
    founder = Mock()
    household = household_after_allocation
    shares = [{"citizen": founder, "amount": 100}]

    # When
    household._fund_company(4, shares)

    # Then
    founder.fund_company.assert_called_once_with(4, 100)


# ---------------------------------------------------
# DEPOSIT MANAGEMENT
# ----------------------------------------------------


@pytest.fixture
def banks(make_dlist):
    # Given
    return make_dlist([Mock(id=i, defaulted=False) for i in range(3)])


@pytest.fixture
def household_before_bank_choice(household, model, depositor_role, banks):
    # Given
    depositor_role.find_deposits.return_value = []
    depositor_role.find_deposit_banks.return_value = banks
    model.random.choice.side_effect = lambda x: x[-1]
    return household


def test_choose_deposit_bank_leave_old_deposit_bank(
    household_before_bank_choice,
    depositor_role,
):
    # Given
    deposit = {"deposit_bank": Mock(id=4), " amount": 100}
    household = household_before_bank_choice
    depositor_role.find_deposits.return_value = [deposit]

    # When
    household._choose_deposit_bank()

    # Then
    depositor_role.leave_deposit_bank.assert_called_once_with(4)


def test_choose_deposit_bank_join_new_deposit_bank(
    household_before_bank_choice,
    depositor_role,
    banks,
):
    # Given
    household = household_before_bank_choice

    # When
    household._choose_deposit_bank()

    # Then
    depositor_role.join_deposit_bank.assert_called_once_with(banks[-1].id)


def test_choose_deposit_bank_doesnt_join_defaulted_bank(
    household_before_bank_choice,
    depositor_role,
    banks,
):
    # Given
    household = household_before_bank_choice
    banks.defaulted = True

    # When
    household._choose_deposit_bank()

    # Then
    depositor_role.join_deposit_bank.assert_not_called()


def test_choose_deposit_bank_join_returns_choice_id(
    household_before_bank_choice, banks
):
    # Given
    household = household_before_bank_choice

    # When
    bank_id = household._choose_deposit_bank()

    # Then
    assert bank_id == banks[-1].id


def test_make_deposits_with_residual_cash(household, account, depositor_role):
    # Given
    bank_id = 2
    account["cash"] = 500

    # When
    household._make_deposits(bank_id)

    # Then
    depositor_role.make_deposits.assert_called_with(2, 500)


@pytest.mark.parametrize("target, expected", [(50, 50), (150, 100)])
def test_withdraw_deposits_finds_and_uses_deposits(
    household,
    depositor_role,
    target,
    expected,
):
    # Given
    deposit = {"deposit_bank": Mock(id=4), "amount": 100}
    depositor_role.find_deposits.return_value = [deposit]

    # When
    household._withdraw_deposits(target)

    # Then
    depositor_role.withdraw_deposits.assert_called_once_with(4, expected)


# ---------------------------------------------------
# HISTORY
# ----------------------------------------------------


def test_update_labor_history_sets_prev_labor_sold(household, worker_role):
    # Given
    worker_role.labor_sold = 0.9

    # When
    household.update_labor_history()

    # Then
    assert household.prev_labor_sold == worker_role.labor_sold


# ---------------------------------------------------
#  OBSERVATION
# ----------------------------------------------------


@pytest.fixture
def household_before_record(household, trad_consumer_role, non_trad_consumer_role):
    # Given
    trad_consumer_role.purchases = 100
    non_trad_consumer_role.purchases = 200
    return household


def test_record_indicators_records_exports_if_tradable(
    household_before_record, trad_consumer_role
):
    # Given
    household = household_before_record

    # When
    household.record_indicators()

    # Then
    assert household.log["imports"][-1] == trad_consumer_role.purchases
