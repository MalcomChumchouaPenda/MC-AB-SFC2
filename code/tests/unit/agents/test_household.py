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

    # When
    is_derived = issubclass(Household, EcoAgent)

    # Then
    assert is_derived


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_wage = 0.0
    model.nprandom = Mock()
    return model


def test_initializes_labor_supply(model):
    # When
    household = Household(model)

    # Then
    assert household.labor_supply == 1.0


def test_initializes_prev_labor_sold(model):
    # When
    household = Household(model)

    # Then
    assert household.prev_labor_sold == 0.0


def test_initializes_preference_randomly(model):
    # Given
    random = model.nprandom
    random.uniform.return_value = 0.4

    # When
    household = Household(model)

    # Then
    random.uniform.assert_called_with(0, math.radians(360))
    assert household.preference == 0.4


def test_initializes_reservation_wage(model):
    # Given
    model.p.initial_wage = 10

    # When
    household = Household(model)

    # Then
    assert household.reservation_wage == 10


def test_initializes_expected_consumption(model):
    # When
    household = Household(model)

    # Then
    assert household.expected_consumption == 0


def test_initializes_desired_consumption(model):
    # When
    household = Household(model)

    # Then
    assert household.desired_consumption == 0


def test_initializes_desired_equity(model):
    # When
    household = Household(model)

    # Then
    assert household.desired_equity == 0


def test_initializes_desired_deposits(model):
    # When
    household = Household(model)

    # Then
    assert household.desired_deposits == 0


def test_initializes_desired_investment_sector(model):
    # When
    household = Household(model)

    # Then
    assert household.desired_investment_sector is None


def test_initializes_net_worth(model):
    # When
    household = Household(model)

    # Then
    assert household.net_worth == 0


def test_initializes_incomes(model):
    # When
    household = Household(model)

    # Then
    assert household.income == 0
    assert household.disposable_income == 0


def test_initializes_deposit_bank_id(model):
    # When
    household = Household(model)

    # Then
    assert household.deposit_bank_id is None


# ----------------------------------------------------
# JOB SEARCH
# ----------------------------------------------------


@pytest.fixture
def household(model):
    # Given
    model.random = Mock()
    model.nprandom = Mock()
    return Household(model)


@pytest.fixture
def hh_with_roles_and_account(household):
    # Given
    roles = {}
    account = {}
    household.roles = roles
    household.account = account
    return household, roles, account


@pytest.fixture
def hh_unemployed(hh_with_roles_and_account):
    # Given
    household, roles, _ = hh_with_roles_and_account
    household.p.psi = 6
    household.labor_supply = 1.0
    household.reservation_wage = 10
    role = Mock(labor_supply=1.0, labor_sold=0.0)
    role.find_employers.return_value = []
    roles["worker"] = role
    return household


def test_search_jobs_with_limited_size(hh_unemployed):
    # Given
    household = hh_unemployed
    role = household.roles["worker"]

    # When
    household.search_jobs()

    # Then
    role.find_employers.assert_called_with(household.p.psi)


def test_search_jobs_with_highest_wage(hh_unemployed):
    # Given
    employer1 = Mock(wage=15, labor_demand=1.0)
    employer2 = Mock(wage=20, labor_demand=1.0)
    household = hh_unemployed
    role = household.roles["worker"]
    role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.accept_job.assert_called_with(employer2, pytest.approx(1.0))


def test_search_jobs_with_sufficient_wage_offered(hh_unemployed):
    # Given
    employer1 = Mock(wage=8, labor_demand=1.0)
    employer2 = Mock(wage=9, labor_demand=1.0)
    household = hh_unemployed
    role = household.roles["worker"]
    role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.accept_job.assert_not_called()


def test_search_jobs_and_split_labor_between_employers(hh_unemployed):
    # Given
    employer1 = Mock(wage=20, labor_demand=0.4)
    employer2 = Mock(wage=15, labor_demand=0.6)
    household = hh_unemployed
    role = household.roles["worker"]
    role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.accept_job.assert_any_call(employer1, pytest.approx(0.4))
    role.accept_job.assert_any_call(employer2, pytest.approx(0.6))


def test_search_jobs_while_labor_supply_is_remaining(hh_unemployed):
    # Given
    employer1 = Mock(wage=25, labor_demand=0.7)
    employer2 = Mock(wage=20, labor_demand=0.7)
    household = hh_unemployed
    role = household.roles["worker"]
    role.labor_supply = 0.5
    role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.accept_job.assert_any_call(employer1, pytest.approx(0.5))


# ---------------------------------------------------
# WAGE REVISION
# ----------------------------------------------------


def test_calc_revision_probability(hh_with_roles_and_account):
    # Given
    role = Mock()
    role.get_unemployment.return_value = 0.1
    household, roles, _ = hh_with_roles_and_account
    household.p.upsilon = 1.0
    roles["worker"] = role

    # When
    result = household._calc_revision_probability()

    # Then
    assert result == math.exp(-1.0 * 0.1)


@pytest.fixture
def fully_employed_before(hh_with_roles_and_account):
    # Given
    household, *_ = hh_with_roles_and_account
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
def part_employed_before(hh_with_roles_and_account):
    # Given
    household, *_ = hh_with_roles_and_account
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
def hh_as_taxpayer(hh_with_roles_and_account):
    # Given
    role = Mock()
    role.get_tax_rate.return_value = 0.2
    household, roles, _ = hh_with_roles_and_account
    roles["citizen"] = role
    return household, role


def test_calc_income(hh_as_taxpayer):
    # Given
    household, _ = hh_as_taxpayer
    household.account["wages"] = 110
    household.account["dep_interests"] = 20
    household.account["dividends"] = 30

    # When
    income = household._calc_income()

    # Then
    assert income == 160


def test_calc_disposable_income(hh_as_taxpayer):
    # Given
    household, _ = hh_as_taxpayer
    household.income = 200
    household.account["public_transfers"] = 50

    # When
    disposable_income = household._calc_disposable_income()

    # Then
    assert disposable_income == 210


def test_pay_taxes_transfers_cash(hh_as_taxpayer):
    # Given
    household, role = hh_as_taxpayer
    household._calc_income = Mock(return_value=100)
    household._calc_disposable_income = Mock(return_value=110)

    # When
    household.pay_taxes()

    # Then
    role.pay_taxes.assert_called_with(20)


def test_pay_taxes_updates_indicators(hh_as_taxpayer):
    # Given
    household, _ = hh_as_taxpayer
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


def test_calc_consumption_updates_choice(hh_with_roles_and_account):
    # Given
    household, _, account = hh_with_roles_and_account
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
def hh_as_specific_consumer(hh_with_roles_and_account):
    # Given
    role = Mock()
    role.get_average_price.return_value = 1
    role.find_suppliers.return_value = []
    household, _, account = hh_with_roles_and_account
    household.p.psi = 1
    account["cash"] = 1000
    return household, role, account


def test_calc_supplier_score_with_salop_formula(hh_as_specific_consumer):
    # Given
    household, *_ = hh_as_specific_consumer
    household.p.beta = 1
    household.preference = 0
    supplier = Mock(variety=0.5, price=10)

    # When
    score = household._calc_supplier_score(supplier, average_price=20)

    # Then
    expected_distance = math.sin(0.5 / 2)
    assert score == (1 / expected_distance) * (20 / 10)


def test_rank_suppliers_using_supplier_score(hh_as_specific_consumer):
    # Given
    method = lambda supplier, average_price: average_price / supplier.price
    household, *_ = hh_as_specific_consumer
    household._calc_supplier_score = method
    suppliers = [Mock(price=i, variety=1) for i in range(1, 3)]

    # When
    ranked = household._rank_suppliers(suppliers, average_price=10)

    # Then
    assert ranked[0].price == 1
    assert ranked[1].price == 2


def test_consume_good_with_found_suppliers(hh_as_specific_consumer):
    # Given
    found = [Mock(price=5, inventories=10) for _ in range(5)]
    household, role, _ = hh_as_specific_consumer
    household.p.psi = 5
    household._rank_suppliers = Mock(return_value=found)
    role.find_suppliers.return_value = found
    role.get_average_price.return_value = 20

    # When
    household._consume_good(role, 100)

    # Then
    role.find_suppliers.assert_called_with(5)
    household._rank_suppliers.assert_any_call(found, average_price=20)


def test_consume_good_with_ranked_suppliers(hh_as_specific_consumer):
    # Given
    ranked = [Mock(price=5, inventories=10) for _ in range(2)]
    household, role, _ = hh_as_specific_consumer
    household._rank_suppliers = Mock(return_value=ranked)

    # When
    household._consume_good(role, 100)

    # Then
    role.buy_goods.assert_any_call(ranked[0], 10)
    role.buy_goods.assert_any_call(ranked[1], 10)
    assert role.buy_goods.call_count == 2


def test_consume_good_with_desired_consumption(hh_as_specific_consumer):
    # Given
    ranked = [Mock(price=5, inventories=10) for _ in range(2)]
    household, role, _ = hh_as_specific_consumer
    household._rank_suppliers = Mock(return_value=ranked)

    # When
    household._consume_good(role, 50)

    # Then
    role.buy_goods.assert_any_call(ranked[0], 10)
    assert role.buy_goods.call_count == 1


def test_consume_good_with_supply_constraints(hh_as_specific_consumer):
    # Given
    ranked = [Mock(price=5, inventories=5) for _ in range(2)]
    household, role, _ = hh_as_specific_consumer
    household._rank_suppliers = Mock(return_value=ranked)

    # When
    household._consume_good(role, 100)

    # Then
    role.buy_goods.assert_any_call(ranked[0], 5)
    role.buy_goods.assert_any_call(ranked[1], 5)
    assert role.buy_goods.call_count == 2


def test_consume_good_with_monetary_constraints(hh_as_specific_consumer):
    # Given
    ranked = [Mock(price=5, inventories=10) for _ in range(2)]
    household, role, account = hh_as_specific_consumer
    household._rank_suppliers = Mock(return_value=ranked)
    account["cash"] = 50

    # When
    household._consume_good(role, 100)

    # Then
    role.buy_goods.assert_any_call(ranked[0], 10)
    assert role.buy_goods.call_count == 1


@pytest.fixture
def hh_as_general_consumer(hh_with_roles_and_account):
    # Given
    household, roles, account = hh_with_roles_and_account
    household._consume_good = Mock()
    roles["depositor"] = Mock()
    roles["trad_consumer"] = Mock()
    roles["non_trad_consumer"] = Mock()
    account["cash"] = 0
    account["deposits"] = 0
    return household, roles, account


def test_consume_each_good_type(hh_as_general_consumer):
    # Given
    household, roles, _ = hh_as_general_consumer
    household.p.cT = 0.6
    household.desired_consumption = 100
    # When
    household.consume()

    # Then
    household._consume_good.assert_any_call(roles["trad_consumer"], 60.0)
    household._consume_good.assert_any_call(roles["non_trad_consumer"], 40.0)


def test_consume_randomizes_entry_order(hh_as_general_consumer):
    # Given
    entry_order = [("trad_consumer", 0.6), ("non_trad_consumer", 0.4)]
    household, *_ = hh_as_general_consumer
    household.p.cT = 0.6
    household.desired_consumption = 100
    random = household.model.random

    # When
    household.consume()

    # Then
    random.shuffle.assert_called_with(entry_order)


def test_consume_withdraws_deposits(hh_as_general_consumer):
    # Given
    household, roles, account = hh_as_general_consumer
    household.p.cT = 0.6
    household.desired_consumption = 100
    household.deposit_bank_id = 5
    account["deposits"] = 100
    account["cash"] = 50
    role = roles["depositor"]

    # When
    household.consume()

    # Then
    role.withdraw_deposits.assert_called_with(5, 50)
    assert household._consume_good.call_count == 2


def test_consume_withdraws_sufficient_deposits(hh_as_general_consumer):
    # Given
    household, roles, account = hh_as_general_consumer
    household.p.cT = 0.6
    household.desired_consumption = 100
    household.deposit_bank_id = 5
    account["deposits"] = 25
    account["cash"] = 50
    role = roles["depositor"]

    # When
    household.consume()

    # Then
    role.withdraw_deposits.assert_called_with(5, 25)
    assert household._consume_good.call_count == 2


def test_consume_withdraws_no_deposits(hh_as_general_consumer):
    # Given
    household, roles, account = hh_as_general_consumer
    household.p.cT = 0.6
    household.desired_consumption = 100
    household.deposit_bank_id = None
    account["deposits"] = 25
    account["cash"] = 50
    role = roles["depositor"]

    # When
    household.consume()

    # Then
    role.withdraw_deposits.assert_not_called()
    assert household._consume_good.call_count == 2


# ---------------------------------------------------
# PORTFOLIO ALLOCATION
# ----------------------------------------------------


@pytest.fixture
def hh_before_allocation(hh_with_roles_and_account):
    # Given
    household, roles, _ = hh_with_roles_and_account
    household.deposit_bank_id = 1
    roles["citizen"] = Mock()
    roles["depositor"] = Mock()
    return household


def test_calc_net_worth(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account["deposits"] = 200
    household.account["equities"] = 300
    household.account["cash"] = 500

    # When
    household._calc_net_worth()

    # Then
    assert household.net_worth == 1000


def test_calc_expected_net_worth(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.net_worth = 1000
    household.disposable_income = 300
    household.expected_consumption = 200

    # When
    expected_worth = household._calc_expected_net_worth()

    # Then
    assert expected_worth == 1100


def test_calc_liquidity_pref_with_deposit_bank_rate(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account["dividends"] = 10
    household.account["equities"] = 100
    household.p.lambda_ = 0.6
    roles = household.roles
    roles["citizen"].get_prob_failure.return_value = 0.10
    roles["depositor"].get_deposit_rate.return_value = 0.05

    # When
    household._calc_liquidity_preference()

    # Then
    roles["depositor"].get_deposit_rate.assert_called_with()


def test_calc_liquidity_pref_when_equity_is_more_profitable(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account["dividends"] = 10
    household.account["equities"] = 100
    household.p.lambda_ = 0.6
    roles = household.roles
    roles["citizen"].get_prob_failure.return_value = 0.10
    roles["depositor"].get_deposit_rate.return_value = 0.05
    expected = 0.6 * math.exp(((10 * (1 - 0.10)) / 100) - 0.05)

    # When
    lp = household._calc_liquidity_preference()

    # Then
    assert lp == pytest.approx(expected)


def test_calc_liquidity_pref_when_equity_is_less_profitable(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account["dividends"] = 2
    household.account["equities"] = 100
    household.p.lambda_ = 0.7
    roles = household.roles
    roles["citizen"].get_prob_failure.return_value = 0.10
    roles["depositor"].get_deposit_rate.return_value = 0.05

    # When
    lp = household._calc_liquidity_preference()

    # Then
    assert lp == 0.7


def test_calc_liquidity_preference_when_no_equity(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account["dividends"] = 0
    household.account["equities"] = 0
    household.p.lambda_ = 0.8
    roles = household.roles
    roles["citizen"].get_prob_failure.return_value = 0.10
    roles["depositor"].get_deposit_rate.return_value = 0.05

    # When
    lp = household._calc_liquidity_preference()

    # Then
    assert lp == 0.8


def test_choose_portfolio_allocation_calc_net_worth(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account["equities"] = 80
    household._calc_liquidity_preference = Mock(return_value=0.80)
    household._calc_expected_net_worth = Mock(return_value=100)
    household._calc_net_worth = Mock()

    # When
    household.choose_portfolio_allocation()

    # Then
    household._calc_net_worth.assert_called_once_with()


def test_choose_portfolio_allocation_updates_desired_assets(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account["equities"] = 20
    household._calc_liquidity_preference = Mock(return_value=0.40)
    household._calc_expected_net_worth = Mock(return_value=100)
    household._calc_net_worth = Mock()

    # When
    household.choose_portfolio_allocation()

    # Then
    assert household.desired_equity == 60
    assert household.desired_deposits == 60


def test_choose_portfolio_allocation_preserves_existing_equity(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account["equities"] = 80
    household._calc_liquidity_preference = Mock(return_value=0.80)
    household._calc_expected_net_worth = Mock(return_value=100)
    household._calc_net_worth = Mock()

    # When
    household.choose_portfolio_allocation()

    # Then
    assert household.desired_equity == 80


def test_choose_portfolio_allocation_updates_citizen_role(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account["equities"] = 80
    household._calc_liquidity_preference = Mock(return_value=0.80)
    household._calc_expected_net_worth = Mock(return_value=100)
    household._calc_net_worth = Mock()
    role = household.roles["citizen"]

    # When
    household.choose_portfolio_allocation()

    # Then
    assert role.resid_equity == 80


# ---------------------------------------------------
# FIRM AND BANK CREATION
# ----------------------------------------------------


@pytest.fixture
def hh_with_investment_steps(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household._choose_investment_sector = Mock()
    household._calc_initial_equity = Mock()
    household._collect_equity_shares = Mock()
    household._create_company = Mock()
    return household


def test_invest_equity_does_nothing_if_no_desired_equity(hh_with_investment_steps):
    # Given
    household = hh_with_investment_steps
    household.desired_equity = 0

    # When
    household.invest_equity()

    # Then
    household._choose_investment_sector.assert_not_called()
    household._calc_initial_equity.assert_not_called()
    household._collect_equity_shares.assert_not_called()
    household._create_company.assert_not_called()


def test_invest_equity_chooses_investment_sector(hh_with_investment_steps):
    # Given
    household = hh_with_investment_steps
    household.desired_equity = 100

    # When
    household.invest_equity()

    # Then
    household._choose_investment_sector.assert_called_once_with()


def test_invest_equity_calcs_initial_equity_with_sector(hh_with_investment_steps):
    # Given
    household = hh_with_investment_steps
    household.desired_equity = 100
    household._choose_investment_sector.return_value = "ANY"

    # When
    household.invest_equity()

    # Then
    household._calc_initial_equity.assert_called_once_with("ANY")


def test_invest_equity_collects_equity_shares_with_target(hh_with_investment_steps):
    # Given
    household = hh_with_investment_steps
    household.desired_equity = 100
    household._calc_initial_equity.return_value = 250

    # When
    household.invest_equity()

    # Then
    household._collect_equity_shares.assert_called_once_with(250)


def test_invest_equity_creates_company_with_sector_and_shares(hh_with_investment_steps):
    # Given
    shares = [Mock()]
    household = hh_with_investment_steps
    household.desired_equity = 100
    household._collect_equity_shares.return_value = shares
    household._choose_investment_sector.return_value = "ANY"

    # When
    household.invest_equity()

    # Then
    household._create_company.assert_called_once_with("ANY", shares)


def test_invest_equity_doesnt_create_company_if_no_shares(hh_with_investment_steps):
    # Given
    household = hh_with_investment_steps
    household.desired_equity = 100
    household._collect_equity_shares.return_value = None
    household._choose_investment_sector.return_value = "ANY"

    # When
    household.invest_equity()

    # Then
    household._create_company.assert_not_called()


@pytest.fixture
def hh_as_investor(hh_before_allocation):
    # Given
    role = Mock()
    household = hh_before_allocation
    household.model.nprandom = Mock()
    household.roles = {"citizen": role}
    return household, role


@pytest.mark.parametrize("ratio1, ratio2", [(0.2, 0.5), (0.5, 0.2)])
def test_choose_investment_sector_returns_bank_sector(hh_as_investor, ratio1, ratio2):
    # Given
    household, role = hh_as_investor
    household.p.cT = 0.6
    household.p.eta = 0.3
    role.get_bank_number_ratio.return_value = ratio1
    role.get_bank_equity_ratio.return_value = ratio2

    # When
    sector = household._choose_investment_sector()

    # Then
    assert sector == "B"


def test_choose_investment_sector_returns_random_firm_sector(hh_as_investor):
    # Given
    household, role = hh_as_investor
    household.p.cT = 0.6
    household.p.eta = 0.3
    role.get_bank_number_ratio.return_value = 0.6
    role.get_bank_equity_ratio.return_value = 0.6
    random = household.model.nprandom

    # When
    sector = household._choose_investment_sector()

    # Then
    random.choice.assert_called_with(["FNT", "FT"], p=[0.4, 0.6])
    assert sector == random.choice.return_value


@pytest.mark.parametrize("ratio", [0.2, 0.5, 0.6])
def test_choose_investment_sector_registers_desired_sector(hh_as_investor, ratio):
    # Given
    household, role = hh_as_investor
    household.p.cT = 0.6
    household.p.eta = 0.3
    role.get_bank_number_ratio.return_value = ratio
    role.get_bank_equity_ratio.return_value = ratio

    # When
    sector = household._choose_investment_sector()

    # Then
    assert household.desired_investment_sector == sector


def test_calc_initial_equity_chooses_equity_between_current_range(hh_as_investor):
    # Given
    household, role = hh_as_investor
    household.p.sigma = 1.0
    random = household.model.nprandom
    role.get_equity_range.return_value = (100, 500)

    # When
    equity = household._calc_initial_equity("ANY")

    # Then
    role.get_equity_range.assert_called_with("ANY")
    random.uniform.assert_called_once_with(100, 500)
    assert equity == random.uniform.return_value


def test_calc_initial_equity_returns_initial_equity_if_no_current_range(hh_as_investor):
    # Given
    household, role = hh_as_investor
    household.p.sigma = 1.0
    household.p.initial_equity = 1000
    random = household.model.nprandom
    role.get_equity_range.return_value = None

    # When
    equity = household._calc_initial_equity("ANY")

    # Then
    random.uniform.assert_not_called()
    assert equity == household.p.initial_equity


def test_calc_initial_equity_includes_median_firm_size_for_bank_sector(hh_as_investor):
    # Given
    household, role = hh_as_investor
    household.p.sigma = 0.5
    random = household.model.nprandom
    role.get_median_firm_size.return_value = 500
    role.get_equity_range.return_value = (100, 500)

    # When
    equity = household._calc_initial_equity("B")

    # Then
    role.get_median_firm_size.assert_called_once_with()
    random.uniform.assert_called_once_with(250, 500)
    assert equity == random.uniform.return_value


def test_calc_initial_equity_uses_median_firm_size_if_no_bank_sector(hh_as_investor):
    # Given
    household, role = hh_as_investor
    household.p.sigma = 0.5
    household.p.initial_equity = 1000
    random = household.model.nprandom
    role.get_median_firm_size.return_value = 500
    role.get_equity_range.return_value = None

    # When
    equity = household._calc_initial_equity("B")

    # Then
    role.get_median_firm_size.assert_called_once_with()
    random.uniform.assert_called_once_with(250, 1000)
    assert equity == random.uniform.return_value


@pytest.fixture
def investors(hh_as_investor):
    # Given
    investors = [Mock(resid_equity=10, company_number=i) for i in range(2)]
    _, role = hh_as_investor
    role.resid_equity = 10
    role.find_investors.return_value = investors
    return investors


@pytest.fixture
def before_equity_collection(hh_as_investor, investors):
    # Given
    household, role = hh_as_investor
    household.p.omega = 0.1
    household.p.psi = 5
    role.get_average_wage.return_value = 15.0
    return household, role, investors


def test_collect_equity_shares_builds_and_returns_shares(before_equity_collection):
    # Given
    household, role, investors = before_equity_collection
    founders = [role] + investors

    # When
    result = household._collect_equity_shares(30)

    # Then
    assert result == [{"founder": founder, "amount": 10} for founder in founders]


def test_collect_equity_shares_with_an_minimum_equity_target(before_equity_collection):
    # Given
    household, role, investors = before_equity_collection
    founders = [role, investors[0]]

    # When
    result = household._collect_equity_shares(15.0)

    # Then
    assert result == [{"founder": founder, "amount": 10} for founder in founders]


def test_collect_equity_shares_returns_none_if_low_funds(before_equity_collection):
    # Given
    household, *_ = before_equity_collection

    # When
    result = household._collect_equity_shares(100.0)

    # Then
    assert result is None


def test_collect_equity_shares_with_minimum_level_of_equity(before_equity_collection):
    # Given
    household, role, investors = before_equity_collection
    ineligible, eligible = investors
    ineligible.resid_equity = 0.5
    founders = [role, eligible]

    # When
    result = household._collect_equity_shares(20)

    # Then
    assert result == [{"founder": founder, "amount": 10} for founder in founders]


def test_collect_equity_shares_with_maximum_company_number(before_equity_collection):
    # Given
    household, role, investors = before_equity_collection
    ineligible, eligible = investors
    ineligible.company_number = 6
    founders = [role, eligible]

    # When
    result = household._collect_equity_shares(20)

    # Then
    assert result == [{"founder": founder, "amount": 10} for founder in founders]


FakeFirm = Mock()


@pytest.fixture
def before_firm_creation(monkeypatch, hh_as_investor):
    # Given
    monkeypatch.setattr("model.agents.household.Firm", FakeFirm)
    household, role = hh_as_investor
    household.p.initial_wage = 1.0
    household.p.initial_productivity = 1.0
    household.model.union = Mock()
    household.model.firms = []
    role.get_productivity_range.return_value = [0, 0]
    role.get_price_range.return_value = [0, 0]
    role.get_sales_range.return_value = [0, 0]
    role.get_wage_range.return_value = [0, 0]
    shares = [{"founder": role, "amount": 100}]
    return household, role, shares


def test_create_company_creates_firm_with_model(before_firm_creation):
    # Given
    household, _, shares = before_firm_creation

    # When
    household._create_company("ANY", shares)

    # Then
    FakeFirm.assert_called_with(household.model)


def test_create_company_sets_new_firm_country_pos(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, _, shares = before_firm_creation
    household.country_pos = 5

    # When
    household._create_company("ANY", shares)

    # Then
    assert firm.country_pos == 5


@pytest.mark.parametrize("sector, tradable", [("FT", True), ("FNT", False)])
def test_create_company_sets_new_firm_tradable(before_firm_creation, sector, tradable):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, _, shares = before_firm_creation

    # When
    household._create_company(sector, shares)

    # Then
    assert firm.tradable == tradable


def test_create_company_sets_new_firm_productivity_from_range(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, role, shares = before_firm_creation
    random = household.model.nprandom
    random.uniform = lambda a, b: (a + b) / 2
    role.get_productivity_range.return_value = (1.0, 2.0)

    # When
    household._create_company("ANY", shares)

    # Then
    assert firm.initial_productivity == pytest.approx(1.5)


def test_create_company_sets_new_firm_productivity_from_params(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, role, shares = before_firm_creation
    household.p.initial_productivity = 0.5
    role.get_productivity_range.return_value = None

    # When
    household._create_company("ANY", shares)

    # Then
    assert firm.initial_productivity == pytest.approx(0.5)


def test_create_company_sets_new_firm_price_from_range(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, role, shares = before_firm_creation
    random = household.model.nprandom
    random.uniform = lambda a, b: (a + b) / 2
    role.get_price_range.return_value = (5.0, 15.0)

    # When
    household._create_company("ANY", shares)

    # Then
    assert firm.price == pytest.approx(10.0)


def test_create_company_sets_new_firm_price_from_params(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, role, shares = before_firm_creation
    household.p.initial_wage = 2.0
    household.p.initial_productivity = 0.5
    role.get_productivity_range.return_value = None

    # When
    household._create_company("ANY", shares)

    # Then
    assert firm.price == pytest.approx(2.0 / 0.5)


def test_create_company_sets_new_firm_sales_from_range(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, role, shares = before_firm_creation
    random = household.model.nprandom
    random.uniform = lambda a, b: (a + b) / 2
    role.get_sales_range.return_value = (50.0, 100.0)

    # When
    household._create_company("ANY", shares)

    # Then
    assert firm.expected_sales == pytest.approx(75.0)


def test_create_company_sets_new_firm_sales_from_params(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, role, shares = before_firm_creation
    household.p.initial_wage = 2.0
    household.p.initial_productivity = 0.5
    role.get_productivity_range.return_value = None

    # When
    household._create_company("ANY", shares)

    # Then
    assert firm.expected_sales == pytest.approx(0.5 * 100 / 2.0)


def test_create_company_sets_new_firm_wage_from_range(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, role, shares = before_firm_creation
    random = household.model.nprandom
    random.uniform = lambda a, b: (a + b) / 2
    role.get_wage_range.return_value = (2.0, 4.0)

    # When
    household._create_company("ANY", shares)

    # Then
    assert firm.wage_offer == pytest.approx(3.0)


def test_create_company_sets_new_firm_wage_from_params(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, role, shares = before_firm_creation
    household.p.initial_wage = 2.0
    role.get_productivity_range.return_value = None

    # When
    household._create_company("ANY", shares)

    # Then
    assert firm.wage_offer == pytest.approx(2.0)


def test_create_company_adds_firm_into_union(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, _, shares = before_firm_creation
    union = household.model.union

    # When
    household._create_company("ANY", shares)

    # Then
    union.add_firm.assert_called_once_with(firm)


def test_create_company_appends_to_model_firms(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, _, shares = before_firm_creation

    # When
    household._create_company("ANY", shares)

    # Then
    assert firm in household.model.firms


def test_create_company_funds_new_firm(before_firm_creation):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household, _, shares = before_firm_creation

    # When
    household._create_company("ANY", shares)

    # Then
    for share in shares:
        share["founder"].fund_company.assert_called_once_with(firm.id, share["amount"])


FakeBank = Mock()


@pytest.fixture
def before_bank_creation(monkeypatch, hh_as_investor):
    # Given
    monkeypatch.setattr("model.agents.household.Bank", FakeBank)
    household, role = hh_as_investor
    household.model.union = Mock()
    household.model.banks = []
    shares = [{"founder": role, "amount": 100}]
    return household, shares


def test_create_company_creates_bank_with_model(before_bank_creation):
    # Given
    household, shares = before_bank_creation

    # When
    household._create_company("B", shares)

    # Then
    FakeBank.assert_called_with(household.model)


def test_create_company_sets_new_bank_country_pos(before_bank_creation):
    # Given
    bank = Mock()
    FakeBank.return_value = bank
    household, shares = before_bank_creation
    household.country_pos = 4

    # When
    household._create_company("B", shares)

    # Then
    assert bank.country_pos == 4


def test_create_company_adds_bank_into_union(before_bank_creation):
    # Given
    bank = Mock()
    FakeBank.return_value = bank
    household, shares = before_bank_creation
    union = household.model.union

    # When
    household._create_company("B", shares)

    # Then
    union.add_bank.assert_called_once_with(bank)


def test_create_company_appends_to_model_banks(before_bank_creation):
    # Given
    bank = Mock()
    FakeBank.return_value = bank
    household, shares = before_bank_creation

    # When
    household._create_company("B", shares)

    # Then
    assert bank in household.model.banks


def test_create_company_funds_new_bank(before_bank_creation):
    # Given
    bank = Mock()
    FakeBank.return_value = bank
    household, shares = before_bank_creation

    # When
    household._create_company("B", shares)

    # Then
    for share in shares:
        share["founder"].fund_company.assert_called_once_with(bank.id, share["amount"])


# ---------------------------------------------------
# DEPOSIT BANK CHOICE
# ----------------------------------------------------


@pytest.fixture
def hh_as_depositor(hh_with_roles_and_account):
    # Given
    role = Mock()
    household, roles, _ = hh_with_roles_and_account
    roles["depositor"] = role
    return household, role


def test_make_deposits_with_residual_cash(hh_as_depositor):
    # Given
    household, role = hh_as_depositor
    household.account["cash"] = 500
    household.deposit_bank_id = 2

    # When
    household.make_deposits()

    # Then
    role.make_deposits.assert_called_with(2, 500)


def test_dont_make_deposits_without_deposit_bank_id(hh_as_depositor):
    # Given
    household, role = hh_as_depositor
    household.account["cash"] = 500
    household.deposit_bank_id = None

    # When
    household.make_deposits()

    # Then
    role.make_deposits.assert_not_called()


def test_choose_deposit_bank_leave_old_deposit_bank(hh_as_depositor):
    # Given
    banks = [Mock(id=i) for i in range(3)]
    household, role = hh_as_depositor
    household.deposit_bank_id = 4
    household.model.random.choice.side_effect = lambda x: x[-1]
    role.find_deposit_banks.return_value = banks

    # When
    household.choose_deposit_bank()

    # Then
    role.leave_deposit_bank.assert_called_once_with(4)


def test_choose_deposit_bank_doesnt_leave_null_deposit_bank(hh_as_depositor):
    # Given
    banks = [Mock(id=i) for i in range(3)]
    household, role = hh_as_depositor
    household.deposit_bank_id = None
    household.model.random.choice.side_effect = lambda x: x[-1]
    role.find_deposit_banks.return_value = banks

    # When
    household.choose_deposit_bank()

    # Then
    role.leave_deposit_bank.assert_not_called()


def test_choose_deposit_bank_join_new_deposit_bank(hh_as_depositor):
    # Given
    banks = [Mock(id=i) for i in range(3)]
    household, role = hh_as_depositor
    household.model.random.choice.side_effect = lambda x: x[-1]
    role.find_deposit_banks.return_value = banks

    # When
    household.choose_deposit_bank()

    # Then
    role.join_deposit_bank.assert_called_once_with(banks[-1].id)


def test_choose_deposit_bank_sets_deposit_bank_id(hh_as_depositor):
    # Given
    banks = [Mock(id=i) for i in range(3)]
    household, role = hh_as_depositor
    household.model.random.choice.side_effect = lambda x: x[-1]
    role.find_deposit_banks.return_value = banks

    # When
    household.choose_deposit_bank()

    # Then
    assert household.deposit_bank_id == banks[-1].id


# ---------------------------------------------------
# HISTORY
# ----------------------------------------------------


def test_update_labor_history_sets_prev_labor_sold(hh_with_roles_and_account):
    # Given
    role = Mock(labor_sold=0.9)
    household, roles, _ = hh_with_roles_and_account
    roles["worker"] = role

    # When
    household.update_labor_history()

    # Then
    assert household.prev_labor_sold == role.labor_sold
