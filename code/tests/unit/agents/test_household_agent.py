import math
import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.agents import HouseholdAgent

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecoagent():
    # Given
    from mcabsfc.base import EcoAgent

    # Assert
    assert issubclass(HouseholdAgent, EcoAgent)


def test_has_unit_labor_supply():
    # Given
    model = Mock()
    household = HouseholdAgent(model)

    # Assert
    assert household.labor_supply == 1


# ---------------------------------------------------
# WORKER BEHAVIORS TESTS
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
    employer1 = Mock(wage=15, demand=1.0)
    employer2 = Mock(wage=20, demand=1.0)
    employer3 = Mock(wage=10, demand=1.0)
    household = unemployed
    role = household.roles["worker"]
    role.search_employers.return_value = [employer1, employer2, employer3]

    # When
    household.search_jobs()

    # Then
    role.create_job.assert_called_with(employer2, pytest.approx(1.0))


def test_search_jobs_with_wage_above_reservation_wage(unemployed):
    # Given
    employer1 = Mock(wage=8, demand=1.0)
    employer2 = Mock(wage=9, demand=1.0)
    household = unemployed
    role = household.roles["worker"]
    role.search_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.create_job.assert_not_called()


def test_search_jobs_and_split_labor_between_employers(unemployed):
    # Given
    employer1 = Mock(wage=20, demand=0.4)
    employer2 = Mock(wage=15, demand=0.6)
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
    employer1 = Mock(wage=25, demand=0.7)
    employer2 = Mock(wage=20, demand=0.7)
    employer3 = Mock(wage=15, demand=0.7)
    household = unemployed
    role = household.roles["worker"]
    role.get_labor_sold.return_value = 0.1
    role.search_employers.return_value = [employer1, employer2, employer3]

    # When
    household.search_jobs()

    # Then
    role.create_job.assert_any_call(employer1, pytest.approx(0.7))
    role.create_job.assert_any_call(employer2, pytest.approx(0.2))


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
# INCOME COMPUTATION TESTS
# ----------------------------------------------------


def test_calc_gross_income():
    # Given
    model = Mock()
    household = HouseholdAgent(model)
    household.labor_income = 100
    household.interest_income = 20
    household.dividend_income = 30
    household.rnd_income = 10

    # When
    income = household.calc_gross_income()

    # Then
    assert income == 160
    assert household.gross_income == 160


def test_calc_disposable_income():
    # Given
    model = Mock()
    citizen_role = Mock()
    citizen_role.get_tax_rate.return_value = 0.2
    household = HouseholdAgent(model)
    household.gross_income = 200
    household.public_transfer = 50
    household.roles["citizen"] = citizen_role

    # When
    income = household.calc_disposable_income()

    # Then
    assert income == 210
    assert household.disposable_income == 210


def test_calc_expected_net_worth():
    # Given
    model = Mock()
    household = HouseholdAgent(model)
    household.net_worth = 1000
    household.disposable_income = 300
    household.expected_consumption = 200

    # When
    expected_worth = household.calc_expected_net_worth()

    # Then
    assert expected_worth == 1100


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
def household_with_consumer_role():
    # Given
    model = Mock()
    consumer_role = Mock()
    household = HouseholdAgent(model)
    household.roles["consumer"] = consumer_role
    return household


def test_search_suppliers(household_with_consumer_role):
    # Given
    household = household_with_consumer_role
    household.model.p.psi = 5
    suppliers = [Mock() for _ in range(5)]
    consumer_role = household.roles["consumer"]
    consumer_role.search_suppliers.return_value = suppliers

    # When
    result = household.search_suppliers()

    # Then
    consumer_role.search_suppliers.assert_called_with(5)
    assert result == suppliers


def test_calc_supplier_score_with_salop_formula(household_with_consumer_role):
    # Given
    household = household_with_consumer_role
    household.model.p.beta = 1
    household.location = 0
    supplier = Mock(price=10, location=0.5)

    # When
    score = household.calc_supplier_score(supplier, avg_price=20)

    # Then
    assert score == (1 / 0.5) * (20 / 10)


def test_rank_suppliers_using_supplier_score(household_with_consumer_role):
    # Given
    method = lambda supplier, avg_price: avg_price / supplier.price
    household = household_with_consumer_role
    household.calc_supplier_score = method
    suppliers = [Mock(id=i, price=i) for i in range(1, 3)]

    # When
    ranked = household.rank_suppliers(suppliers, avg_price=10)

    # Then
    assert ranked[0].id == 1
    assert ranked[1].id == 2


def test_consume_with_multiple_steps(household_with_consumer_role):
    # Given
    suppliers = [Mock() for _ in range(5)]
    household = household_with_consumer_role
    household.roles["consumer"].get_average_price.return_value = 20
    household.search_suppliers = Mock(return_value=suppliers)
    household.rank_suppliers = Mock(return_value=suppliers)
    household.buy_goods = Mock()

    # When
    household.consume()

    # Then
    household.search_suppliers.assert_called_with()
    household.rank_suppliers.assert_called_with(suppliers, avg_price=20)
    household.buy_goods.assert_called_once_with(suppliers)
