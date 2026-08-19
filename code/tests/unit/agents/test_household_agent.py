import math
import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import HouseholdAgent

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from mc_ab_sfc.base import EcoAgent

    # Assert
    assert issubclass(HouseholdAgent, EcoAgent)


@pytest.fixture
def household():
    # Given
    model = Mock()
    household = HouseholdAgent(model)
    return household


def test_has_default_stocks(household):
    # Assert
    assert household.cash == 0
    assert household.deposits == 0
    assert household.equity == 0


def test_has_default_flows(household):
    # Assert
    assert household.labor_income == 0
    assert household.deposit_interest == 0
    assert household.dividends == 0
    assert household.rd_income == 0
    assert household.taxes == 0
    assert household.tradable_cons == 0
    assert household.non_tradable_cons == 0
    assert household.public_transfers == 0


def test_has_default_choices(household):
    # Assert
    assert household.reservation_wage == 0
    assert household.expected_consumption == 0
    assert household.desired_trad_cons == 0
    assert household.desired_non_trad_cons == 0
    assert household.desired_equity == 0
    assert household.desired_deposits == 0
    assert household.desired_investment_sector is None


def test_has_default_indicator(household):
    # Assert
    assert household.employed_labor == 0
    assert household.net_worth == 0
    assert household.income == 0
    assert household.disposable_income == 0


def test_has_unit_labor_supply(household):
    # Assert
    assert household.labor_supply == 1


def test_has_default_position(household):
    # Assert
    assert household.position == 0


# ---------------------------------------------------
# JOB SEARCH TESTS
# ----------------------------------------------------


@pytest.fixture
def unemployed():
    # Given
    model = Mock()
    model.p.psi = 6
    role = Mock()
    role.search_employers.return_value = []
    role.get_labor_sold.return_value = 0.0
    household = HouseholdAgent(model)
    household.labor_supply = 1.0
    household.reservation_wage = 10
    household.roles = {"worker": role}
    return household


def test_search_jobs_with_limited_size(unemployed):
    # Given
    household = unemployed
    household.p.psi = 4
    role = household.roles["worker"]

    # When
    household.search_jobs()

    # Then
    role.search_employers.assert_called_with(4)


def test_search_jobs_with_highest_wage(unemployed):
    # Given
    employer1 = Mock(wage_offer=15, labor_demand=1.0)
    employer2 = Mock(wage_offer=20, labor_demand=1.0)
    employer3 = Mock(wage_offer=10, labor_demand=1.0)
    household = unemployed
    role = household.roles["worker"]
    role.search_employers.return_value = [employer1, employer2, employer3]

    # When
    household.search_jobs()

    # Then
    role.create_job.assert_called_with(employer2, pytest.approx(1.0))


def test_search_jobs_with_wage_above_reservation_wage(unemployed):
    # Given
    employer1 = Mock(wage_offer=8, labor_demand=1.0)
    employer2 = Mock(wage_offer=9, labor_demand=1.0)
    household = unemployed
    role = household.roles["worker"]
    role.search_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.create_job.assert_not_called()


def test_search_jobs_and_split_labor_between_employers(unemployed):
    # Given
    employer1 = Mock(wage_offer=20, labor_demand=0.4)
    employer2 = Mock(wage_offer=15, labor_demand=0.6)
    household = unemployed
    role = household.roles["worker"]
    role.search_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.create_job.assert_any_call(employer1, pytest.approx(0.4))
    role.create_job.assert_any_call(employer2, pytest.approx(0.6))


def test_search_jobs_while_labor_supply_is_remaining(unemployed):
    # Given
    employer1 = Mock(wage_offer=25, labor_demand=0.7)
    employer2 = Mock(wage_offer=20, labor_demand=0.7)
    employer3 = Mock(wage_offer=15, labor_demand=0.7)
    household = unemployed
    role = household.roles["worker"]
    role.get_labor_sold.return_value = 0.1
    role.search_employers.return_value = [employer1, employer2, employer3]

    # When
    household.search_jobs()

    # Then
    role.create_job.assert_any_call(employer1, pytest.approx(0.7))
    role.create_job.assert_any_call(employer2, pytest.approx(0.2))


# ---------------------------------------------------
# WAGE REVISION TESTS
# ----------------------------------------------------


def test_calc_revision_probability():
    # Given
    model = Mock()
    model.p.upsilon = 1.0
    model.p.upsilon_h = 0.9
    worker_role = Mock()
    worker_role.get_unemployment_rate.return_value = 0.1
    household = HouseholdAgent(model)
    household.roles["worker"] = worker_role

    # When
    result = household.calc_revision_probability()

    # Then
    assert result == 0.9 * math.exp(-1.0 * 0.1)


@pytest.fixture
def fully_employed_before():
    # Given
    model = Mock()
    model.p.delta = 0.9
    household = HouseholdAgent(model)
    household.labor_supply = 1.0
    household.employed_labor = 1.0
    household.reservation_wage = 10.0
    household.calc_revision_probability = Mock()
    household.calc_revision_probability.return_value = 0
    return household


def test_increases_reservation_wage_when_fully_employed(fully_employed_before):
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


def test_increases_reservation_wage_with_upward_revision_prob(fully_employed_before):
    # Given
    household = fully_employed_before
    household.calc_revision_probability.return_value = 0.6
    random = household.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    random.choice.assert_called_with([0, 1], p=[1 - 0.6, 0.6])


def test_can_choose_to_not_increases_reservation_wage(fully_employed_before):
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
def part_employed_before():
    # Given
    model = Mock()
    model.p.delta = 0.9
    household = HouseholdAgent(model)
    household.labor_supply = 1.0
    household.employed_labor = 0.0
    household.reservation_wage = 10.0
    household.calc_revision_probability = Mock()
    household.calc_revision_probability.return_value = 0
    return household


def test_decreases_reservation_wage_when_not_fully_employed(part_employed_before):
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


def test_decreases_reservation_wage_with_downward_revision_prob(part_employed_before):
    # Given
    household = part_employed_before
    household.calc_revision_probability.return_value = 0.6
    random = household.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 1 - 0.6])


def test_can_choose_to_not_decreases_reservation_wage(part_employed_before):
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
def household_as_taxpayer():
    # Given
    model = Mock()
    household = HouseholdAgent(model)
    household.roles["tax_payer"] = Mock()
    return household


def test_calc_income(household_as_taxpayer):
    # Given
    household = household_as_taxpayer
    household.labor_income = 100
    household.deposit_interest = 20
    household.dividends = 30
    household.rd_income = 10

    # When
    income = household.calc_income()

    # Then
    assert income == 160


def test_calc_disposable_income(household_as_taxpayer):
    # Given
    household = household_as_taxpayer
    household.income = 200
    household.public_transfers = 50
    payer_role = household.roles["tax_payer"]
    payer_role.get_tax_rate.return_value = 0.2

    # When
    disposable_income = household.calc_disposable_income()

    # Then
    assert disposable_income == 210


def test_pay_taxes(household_as_taxpayer):
    # Given
    household = household_as_taxpayer
    household.calc_income = Mock(return_value=100)
    household.calc_disposable_income = Mock(return_value=110)
    payer_role = household.roles["tax_payer"]
    payer_role.get_tax_rate.return_value = 0.2

    # When
    household.pay_taxes()

    # Then
    payer_role.pay_taxes.assert_called_once_with(20)
    assert household.disposable_income == 110
    assert household.income == 100


# ---------------------------------------------------
# CONSUMPTION BEHAVIOR TESTS
# ----------------------------------------------------


def test_calc_consumption_total():
    # Given
    model = Mock()
    model.p.cy = 0.8
    model.p.cd = 0.1
    model.p.cT = 0.6
    household = HouseholdAgent(model)
    household.disposable_income = 1000
    household.deposits = 500

    # When
    consumption = household.calc_consumption()

    # Then
    assert consumption == 850
    assert household.desired_consumption == 850


def test_calc_consumption_composition():
    # Given
    model = Mock()
    model.p.cy = 0.8
    model.p.cd = 0.1
    model.p.cT = 0.6
    household = HouseholdAgent(model)
    household.disposable_income = 1000
    household.deposits = 500

    # When
    household.calc_consumption()

    # Then
    assert household.desired_trad_cons == 510
    assert household.desired_non_trad_cons == 340


@pytest.fixture
def household_with_consumer_roles():
    # Given
    model = Mock()
    household = HouseholdAgent(model)
    household.roles["consumer_tradable"] = Mock()
    household.roles["consumer_non_tradable"] = Mock()
    return household


def test_calc_supplier_score_with_salop_formula(household_with_consumer_roles):
    # Given
    household = household_with_consumer_roles
    household.model.p.beta = 1
    household.position = 0
    supplier = Mock(position=0.5, price=10)

    # When
    score = household.calc_supplier_score(supplier, average_price=20)

    # Then
    expected_distance = math.sin(0.5 / 2)
    assert score == (1 / expected_distance) * (20 / 10)


def test_rank_suppliers_using_supplier_score(household_with_consumer_roles):
    # Given
    method = lambda supplier, average_price: average_price / supplier.price
    household = household_with_consumer_roles
    household.calc_supplier_score = method
    suppliers = [Mock(id=i, price=i) for i in range(1, 3)]

    # When
    ranked = household.rank_suppliers(suppliers, average_price=10)

    # Then
    assert ranked[0].id == 1
    assert ranked[1].id == 2


def test_consume_tradable_goods_with_steps(household_with_consumer_roles):
    # Given
    suppliers = [Mock() for _ in range(5)]
    ranked_suppliers = [Mock() for _ in range(5)]
    household = household_with_consumer_roles
    household.model.p.psi = 5
    household.rank_suppliers = Mock(return_value=ranked_suppliers)
    consumer_role = household.roles["consumer_tradable"]
    consumer_role.get_average_price.return_value = 20
    consumer_role.search_suppliers.return_value = suppliers

    # When
    household.consume()

    # Then
    consumer_role.search_suppliers.assert_called_with(5)
    household.rank_suppliers.assert_any_call(suppliers, average_price=20)
    consumer_role.buy_goods.assert_called_once_with(ranked_suppliers)


def test_consume_non_tradable_goods_with_steps(household_with_consumer_roles):
    # Given
    suppliers = [Mock() for _ in range(5)]
    ranked_suppliers = [Mock() for _ in range(5)]
    household = household_with_consumer_roles
    household.model.p.psi = 5
    household.rank_suppliers = Mock(return_value=ranked_suppliers)
    consumer_role = household.roles["consumer_non_tradable"]
    consumer_role.get_average_price.return_value = 10
    consumer_role.search_suppliers.return_value = suppliers

    # When
    household.consume()

    # Then
    consumer_role.search_suppliers.assert_called_with(5)
    household.rank_suppliers.assert_any_call(suppliers, average_price=10)
    consumer_role.buy_goods.assert_called_once_with(ranked_suppliers)


def test_consume_randomizes_market_order(household_with_consumer_roles):
    # Given
    household = household_with_consumer_roles
    trad_role = household.roles["consumer_tradable"]
    trad_role.search_suppliers.return_value = []
    non_trad_role = household.roles["consumer_non_tradable"]
    non_trad_role.search_suppliers.return_value = []
    random = household.model.random

    # When
    household.consume()

    # Then
    random.shuffle.assert_called_with([trad_role, non_trad_role])


# ---------------------------------------------------
# PORTFOLIO ALLOCATION TESTS
# ----------------------------------------------------


@pytest.fixture
def household_with_assets():
    # Given
    model = Mock()
    household = HouseholdAgent(model)
    household.roles["equity_holder"] = Mock()
    household.roles["deposit_holder"] = Mock()
    return household


def test_calc_expected_net_worth(household_with_assets):
    # Given
    household = household_with_assets
    household.net_worth = 1000
    household.disposable_income = 300
    household.expected_consumption = 200

    # When
    expected_worth = household.calc_expected_net_worth()

    # Then
    assert expected_worth == 1100


def test_calc_liquidity_pref_when_equity_is_more_profitable(household_with_assets):
    # Given
    household = household_with_assets
    household.dividends = 10
    household.equity = 100
    household.p.lambda_ = 0.6
    roles = household.roles
    roles["equity_holder"].get_default_probability.return_value = 0.10
    roles["deposit_holder"].get_deposit_rate.return_value = 0.05

    # When
    lp = household.calc_liquidity_preference()

    # Then
    expected = 0.6 * math.exp(-((10 * (1 - 0.10)) / 100) - 0.05)
    assert lp == pytest.approx(expected)


def test_calc_liquidity_pref_when_equity_is_less_profitable(household_with_assets):
    # Given
    household = household_with_assets
    household.dividends = 2
    household.equity = 100
    household.p.lambda_ = 0.7
    roles = household.roles
    roles["equity_holder"].get_default_probability.return_value = 0.10
    roles["deposit_holder"].get_deposit_rate.return_value = 0.05

    # When
    lp = household.calc_liquidity_preference()

    # Then
    assert lp == 0.7


def test_calc_liquidity_preference_when_no_equity(household_with_assets):
    # Given
    household = household_with_assets
    household.dividends = 0
    household.equity = 0
    household.p.lambda_ = 0.8
    roles = household.roles
    roles["equity_holder"].get_default_probability.return_value = 0.10
    roles["deposit_holder"].get_deposit_rate.return_value = 0.05

    # When
    lp = household.calc_liquidity_preference()

    # Then
    assert lp == 0.8


def test_calc_portfolio_allocation_updates_desired_assets():
    # Given
    model = Mock()
    household = HouseholdAgent(model)
    household.equity = 20
    household.calc_liquidity_preference = Mock(return_value=0.40)
    household.calc_expected_net_worth = Mock(return_value=100)

    # When
    household.calc_portfolio_allocation()

    # Then
    assert household.desired_equity == 60
    assert household.desired_deposits == 60


def test_calc_portfolio_allocation_preserves_existing_equity():
    # Given
    model = Mock()
    household = HouseholdAgent(model)
    household.equity = 80
    household.calc_liquidity_preference = Mock(return_value=0.80)
    household.calc_expected_net_worth = Mock(return_value=100)

    # When
    household.calc_portfolio_allocation()

    # Then
    assert household.desired_equity == 80


@pytest.fixture
def household_before_investment():
    model = Mock()
    model.p.cT = 0.6
    model.p.eta = 0.3
    household = HouseholdAgent(model)
    household.roles = {"equity_holder": Mock()}
    return household


def test_find_potential_equity_investors(household_before_investment):
    # Given
    investors = [Mock(), Mock()]
    household = household_before_investment
    holder_role = household.roles["equity_holder"]
    holder_role.get_potential_investors.return_value = investors

    # When
    result = household.find_potential_investors()

    # Then
    assert result == investors


@pytest.mark.parametrize("ratio1, ratio2", [(0.2, 0.5), (0.5, 0.2)])
def test_choose_bank_as_investment_sector(household_before_investment, ratio1, ratio2):
    # Given
    household = household_before_investment
    holder_role = household.roles["equity_holder"]
    holder_role.get_bank_firm_number_ratio.return_value = ratio1
    holder_role.get_bank_firm_equity_ratio.return_value = ratio2

    # When
    sector = household.choose_investment_sector()

    # Then
    assert sector == "banks"
    assert household.desired_investment_sector == sector


def test_choose_firm_as_investment_sector(household_before_investment):
    # Given
    household = household_before_investment
    holder_role = household.roles["equity_holder"]
    holder_role.get_bank_firm_number_ratio.return_value = 0.6
    holder_role.get_bank_firm_equity_ratio.return_value = 0.6
    random = household.model.nprandom
    random.choice.return_value = "tradable_firms"
    sectors = ["non_tradable_firms", "tradable_firms"]

    # When
    sector = household.choose_investment_sector()

    # Then
    random.choice.assert_called_with(sectors, p=[0.4, 0.6])
    assert sector == "tradable_firms"
    assert household.desired_investment_sector == sector


@pytest.mark.parametrize("sector", ["non_tradable_firms", "tradable_firms", "banks"])
def test_calc_initial_equity_by_investment_sector(household_before_investment, sector):
    # Given
    household = household_before_investment
    household.desired_investment_sector = sector
    holder_role = household.roles["equity_holder"]
    holder_role.get_sector_equity_range.return_value = (100, 500)
    random = household.model.nprandom
    random.uniform.return_value = 300

    # When
    equity = household.calc_initial_equity(sector)

    # Then
    holder_role.get_sector_equity_range.assert_called_with(sector)
    assert equity == 300


@pytest.mark.parametrize("sector", ["non_tradable_firms", "tradable_firms", "banks"])
def test_calc_initial_equity_uses_exogenous_equity(household_before_investment, sector):
    # Given
    household = household_before_investment
    household.p.initial_equity = 1000
    holder_role = household.roles["equity_holder"]
    holder_role.get_sector_equity_range.return_value = None

    # When
    equity = household.calc_initial_equity(sector=sector)

    # Then
    assert equity == 1000


def test_create_enterprise_can_create_non_tradable_firms(household_before_investment):
    # Given
    household = household_before_investment
    role = household.roles["equity_holder"]
    founders = [Mock() for _ in range(5)]

    # When
    household.create_enterprise(founders, sector="non_tradable_firms")

    # Then
    role.create_firm.assert_called_once_with(founders, tradable=False)


def test_create_enterprise_can_create_tradable_firms(household_before_investment):
    # Given
    household = household_before_investment
    role = household.roles["equity_holder"]
    founders = [Mock() for _ in range(5)]

    # When
    household.create_enterprise(founders, sector="tradable_firms")

    # Then
    role.create_firm.assert_called_once_with(founders, tradable=True)


def test_create_enterprise_can_create_bank(household_before_investment):
    # Given
    household = household_before_investment
    role = household.roles["equity_holder"]
    founders = [Mock() for _ in range(5)]

    # When
    household.create_enterprise(founders, sector="banks")

    # Then
    role.create_bank.assert_called_once_with(founders)


@pytest.fixture
def household_as_investor():
    model = Mock()
    household = HouseholdAgent(model)
    household.desired_equity = 100
    household.roles = {"equity_holder": Mock()}
    household.choose_investment_sector = Mock(return_value=None)
    household.find_potential_investors = Mock(return_value=[])
    household.calc_initial_equity = Mock(return_value=100)
    household.create_enterprise = Mock()
    household.make_deposits = Mock()
    household.withdraw_deposits = Mock()
    return household


def test_invest_equity_does_nothing_without_desire(household_as_investor):
    # Given
    household = household_as_investor
    household.desired_equity = 0

    # When
    household.invest_equity()

    # Then
    household.choose_investment_sector.assert_not_called()
    household.find_potential_investors.assert_not_called()
    household.calc_initial_equity.assert_not_called()
    household.create_enterprise.assert_not_called()


def test_invest_equity_when_sufficient_equity(household_as_investor):
    # Given
    household = household_as_investor
    initiator = household.roles["equity_holder"]
    founders = [Mock(desired_equity=100) for _ in range(2)]
    household.find_potential_investors.return_value = founders
    household.choose_investment_sector.return_value = "any"
    household.calc_initial_equity.return_value = 300

    # When
    household.invest_equity()

    # Then
    household.find_potential_investors.assert_called_with()
    household.calc_initial_equity.assert_called_with("any")
    household.create_enterprise.assert_called_with([initiator] + founders, "any")


def test_invest_equity_with_only_sufficient_equity(household_as_investor):
    # Given
    household = household_as_investor
    initiator = household.roles["equity_holder"]
    founders = [Mock(desired_equity=100) for _ in range(5)]
    household.find_potential_investors.return_value = founders
    household.choose_investment_sector.return_value = "any"
    household.calc_initial_equity.return_value = 300

    # When
    household.invest_equity()

    # Then
    household.find_potential_investors.assert_called_with()
    household.calc_initial_equity.assert_called_with("any")
    household.create_enterprise.assert_called_with([initiator] + founders[:2], "any")


def test_invest_equity_does_nothing_when_insufficient_equity(household_as_investor):
    # Given
    household = household_as_investor
    household.find_potential_investors.return_value = []
    household.choose_investment_sector.return_value = "any"
    household.calc_initial_equity.return_value = 300

    # When
    household.invest_equity()

    # Then
    household.find_potential_investors.assert_called_with()
    household.calc_initial_equity.assert_called_with("any")
    household.create_enterprise.assert_not_called()

