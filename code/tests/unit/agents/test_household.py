import math
import pytest
from unittest.mock import Mock, PropertyMock
from model.agents.household import Household

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from model.base import EcoAgent

    # Assert
    assert issubclass(Household, EcoAgent)


@pytest.fixture
def household_before_setup():
    # Given
    model = Mock()
    household = Household(model)
    return household


# def test_has_default_stocks(household_before_setup):
#     # Given
#     household = household_before_setup

#     # When

#     # Assert
#     assert household.cash == 0
#     assert household.equity == 0


# def test_has_default_flows(household):
#     # Assert
#     assert household.labor_income == 0
#     assert household.dividends == 0
#     assert household.rd_income == 0
#     assert household.taxes == 0
#     assert household.tradable_cons == 0
#     assert household.non_tradable_cons == 0
#     assert household.public_transfers == 0


def test_has_default_reservation_wage(household_before_setup):
    # Given
    household = household_before_setup

    # When
    household.setup()

    # Then
    assert household.reservation_wage == 0


def test_has_default_expected_consumption(household_before_setup):
    # Given
    household = household_before_setup

    # When
    household.setup()

    # Then
    assert household.expected_consumption == 0


def test_has_default_desired_consumption(household_before_setup):
    # Given
    household = household_before_setup

    # When
    household.setup()

    # Then
    assert household.desired_trad_cons == 0
    assert household.desired_non_trad_cons == 0


def test_has_default_desired_equity(household_before_setup):
    # Given
    household = household_before_setup

    # When
    household.setup()

    # Then
    assert household.desired_equity == 0


def test_has_default_desired_deposits(household_before_setup):
    # Given
    household = household_before_setup

    # When
    household.setup()

    # Then
    assert household.desired_deposits == 0


def test_has_default_desired_investment_sector(household_before_setup):
    # Given
    household = household_before_setup

    # When
    household.setup()

    # Then
    assert household.desired_investment_sector is None


def test_has_default_net_worth(household_before_setup):
    # Given
    household = household_before_setup

    # When
    household.setup()

    # Then
    assert household.net_worth == 0


def test_has_default_incomes(household_before_setup):
    # Given
    household = household_before_setup

    # When
    household.setup()

    # Then
    assert household.income == 0
    assert household.disposable_income == 0


# ---------------------------------------------------
# JOB SEARCH TESTS
# ----------------------------------------------------


@pytest.fixture
def household_with_roles(household_before_setup):
    # Given
    roles = {}
    household = household_before_setup
    household.roles = roles
    return household, roles


@pytest.fixture
def household_unemployed(household_with_roles):
    # Given
    household, roles = household_with_roles
    household.p.psi = 6
    household.labor_supply = 1.0
    household.reservation_wage = 10
    role = Mock(labor_supply=1.0, labor_sold=0.0)
    role.find_employers.return_value = []
    roles["worker"] = role
    return household


def test_search_jobs_with_limited_size(household_unemployed):
    # Given
    household = household_unemployed
    role = household.roles["worker"]

    # When
    household.search_jobs()

    # Then
    role.find_employers.assert_called_with(household.p.psi)


def test_search_jobs_with_highest_wage(household_unemployed):
    # Given
    employer1 = Mock(wage=15, labor_demand=1.0)
    employer2 = Mock(wage=20, labor_demand=1.0)
    household = household_unemployed
    role = household.roles["worker"]
    role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.accept_job.assert_called_with(employer2, pytest.approx(1.0))


def test_search_jobs_with_sufficient_wage_offered(household_unemployed):
    # Given
    employer1 = Mock(wage=8, labor_demand=1.0)
    employer2 = Mock(wage=9, labor_demand=1.0)
    household = household_unemployed
    role = household.roles["worker"]
    role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.accept_job.assert_not_called()


def test_search_jobs_and_split_labor_between_employers(household_unemployed):
    # Given
    employer1 = Mock(wage=20, labor_demand=0.4)
    employer2 = Mock(wage=15, labor_demand=0.6)
    household = household_unemployed
    role = household.roles["worker"]
    role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.accept_job.assert_any_call(employer1, pytest.approx(0.4))
    role.accept_job.assert_any_call(employer2, pytest.approx(0.6))


def test_search_jobs_while_labor_supply_is_remaining(household_unemployed):
    # Given
    employer1 = Mock(wage=25, labor_demand=0.7)
    employer2 = Mock(wage=20, labor_demand=0.7)
    household = household_unemployed
    role = household.roles["worker"]
    role.labor_supply = 0.5
    role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.accept_job.assert_any_call(employer1, pytest.approx(0.5))


# ---------------------------------------------------
# WAGE REVISION TESTS
# ----------------------------------------------------


def test_calc_revision_probability(household_with_roles):
    # Given
    role = Mock()
    role.get_unemployment_rate.return_value = 0.1
    household, roles = household_with_roles
    household.p.upsilon = 1.0
    household.p.upsilon_h = 0.9
    roles["worker"] = role

    # When
    result = household.calc_revision_probability()

    # Then
    assert result == 0.9 * math.exp(-1.0 * 0.1)


@pytest.fixture
def fully_employed_before(household_with_roles):
    # Given
    household, _ = household_with_roles
    household.p.delta = 0.9
    household.labor_supply = 1.0
    household.employed_labor = 1.0
    household.reservation_wage = 10.0
    household.calc_revision_probability = Mock()
    household.calc_revision_probability.return_value = 0
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
    household.calc_revision_probability.return_value = 0.6
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
def part_employed_before(household_with_roles):
    # Given
    household, _ = household_with_roles
    household.p.delta = 0.9
    household.labor_supply = 1.0
    household.employed_labor = 0.0
    household.reservation_wage = 10.0
    household.calc_revision_probability = Mock()
    household.calc_revision_probability.return_value = 0
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
    household.calc_revision_probability.return_value = 0.6
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
def mock_dep_interests(monkeypatch):
    # Given
    mock_interests = PropertyMock()
    monkeypatch.setattr(Household, "dep_interests", mock_interests)
    return mock_interests


@pytest.fixture
def model_with_govt():
    # Given
    govt = Mock(tax_rate=0.2, reserves=0, taxes=0)
    model = Mock()
    model.governments = {"any": govt}
    return model, govt


@pytest.fixture
def household_as_taxpayer(mock_dep_interests, model_with_govt):
    # Given
    model, _ = model_with_govt
    household = Household(model)
    household.mock_dep_interests = mock_dep_interests
    household.country = "any"
    return household


def test_calc_income(household_as_taxpayer):
    # Given
    household = household_as_taxpayer
    household.labor_income = 100
    household.mock_dep_interests.return_value = 20
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

    # When
    disposable_income = household.calc_disposable_income()

    # Then
    assert disposable_income == 210


def test_pay_taxes_transfers_cash(household_as_taxpayer, model_with_govt):
    # Given
    _, govt = model_with_govt
    household = household_as_taxpayer
    household.calc_income = Mock(return_value=100)
    household.calc_disposable_income = Mock(return_value=110)

    # When
    household.pay_taxes()

    # Then
    assert household.taxes == 20
    assert household.cash == -20
    assert govt.taxes == 20
    assert govt.reserves == 20


def test_pay_taxes_updates_indicators(household_as_taxpayer):
    # Given
    household = household_as_taxpayer
    household.calc_income = Mock(return_value=100)
    household.calc_disposable_income = Mock(return_value=110)

    # When
    household.pay_taxes()

    # Then
    assert household.disposable_income == 110
    assert household.income == 100


# ---------------------------------------------------
# CONSUMPTION BEHAVIOR TESTS
# ----------------------------------------------------


@pytest.fixture
def mock_deposits(monkeypatch):
    # Given
    mock_deposits = PropertyMock()
    monkeypatch.setattr(Household, "deposits", mock_deposits)
    return mock_deposits


def test_calc_consumption_total(mock_deposits):
    # Given
    model = Mock()
    model.p.cy = 0.8
    model.p.cd = 0.1
    model.p.cT = 0.6
    household = Household(model)
    household.disposable_income = 1000
    mock_deposits.return_value = 500

    # When
    consumption = household.calc_consumption()

    # Then
    assert consumption == 850
    assert household.desired_consumption == 850


def test_calc_consumption_composition(mock_deposits):
    # Given
    model = Mock()
    model.p.cy = 0.8
    model.p.cd = 0.1
    model.p.cT = 0.6
    household = Household(model)
    household.disposable_income = 1000
    mock_deposits.return_value = 500

    # When
    household.calc_consumption()

    # Then
    assert household.desired_trad_cons == 510
    assert household.desired_non_trad_cons == 340


@pytest.fixture
def household_with_consumer_roles(household_with_roles):
    # Given
    household, _ = household_with_roles
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
def hh_before_allocation(household_with_roles):
    # Given
    household, roles = household_with_roles
    household.account = Mock()
    roles["citizen"] = Mock()
    roles["depositor"] = Mock()
    return household


def test_calc_expected_net_worth(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.net_worth = 1000
    household.disposable_income = 300
    household.expected_consumption = 200

    # When
    expected_worth = household.calc_expected_net_worth()

    # Then
    assert expected_worth == 1100


def test_calc_liquidity_pref_when_equity_is_more_profitable(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.dividends = 10
    household.equity = 100
    household.p.lambda_ = 0.6
    roles = household.roles
    roles["citizen"].get_prob_failure.return_value = 0.10
    roles["depositor"].get_deposit_rate.return_value = 0.05

    # When
    lp = household.calc_liquidity_preference()

    # Then
    expected = 0.6 * math.exp(-((10 * (1 - 0.10)) / 100) - 0.05)
    assert lp == pytest.approx(expected)


def test_calc_liquidity_pref_when_equity_is_less_profitable(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.dividends = 2
    household.equity = 100
    household.p.lambda_ = 0.7
    roles = household.roles
    roles["citizen"].get_prob_failure.return_value = 0.10
    roles["depositor"].get_deposit_rate.return_value = 0.05

    # When
    lp = household.calc_liquidity_preference()

    # Then
    assert lp == 0.7


def test_calc_liquidity_preference_when_no_equity(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.dividends = 0
    household.equity = 0
    household.p.lambda_ = 0.8
    roles = household.roles
    roles["citizen"].get_prob_failure.return_value = 0.10
    roles["depositor"].get_deposit_rate.return_value = 0.05

    # When
    lp = household.calc_liquidity_preference()

    # Then
    assert lp == 0.8


def test_calc_portfolio_allocation_updates_desired_assets():
    # Given
    model = Mock()
    household = Household(model)
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
    household = Household(model)
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
    household = Household(model)
    household.roles = {"citizen": Mock()}
    return household


def test_find_potential_equity_investors(household_before_investment):
    # Given
    investors = [Mock(), Mock()]
    household = household_before_investment
    holder_role = household.roles["citizen"]
    holder_role.get_potential_investors.return_value = investors

    # When
    result = household.find_potential_investors()

    # Then
    assert result == investors


@pytest.mark.parametrize("ratio1, ratio2", [(0.2, 0.5), (0.5, 0.2)])
def test_choose_bank_as_investment_sector(household_before_investment, ratio1, ratio2):
    # Given
    household = household_before_investment
    holder_role = household.roles["citizen"]
    holder_role.get_bank_firm_number_ratio.return_value = ratio1
    holder_role.get_bank_firm_equity_ratio.return_value = ratio2

    # When
    sector = household.choose_investment_sector()

    # Then
    assert sector == "B"
    assert household.desired_investment_sector == sector


def test_choose_firm_as_investment_sector(household_before_investment):
    # Given
    household = household_before_investment
    holder_role = household.roles["citizen"]
    holder_role.get_bank_firm_number_ratio.return_value = 0.6
    holder_role.get_bank_firm_equity_ratio.return_value = 0.6
    random = household.model.nprandom
    random.choice.return_value = "FT"
    sectors = ["FNT", "FT"]

    # When
    sector = household.choose_investment_sector()

    # Then
    random.choice.assert_called_with(sectors, p=[0.4, 0.6])
    assert sector == "FT"
    assert household.desired_investment_sector == sector


@pytest.mark.parametrize("sector", ["FNT", "FT", "B"])
def test_calc_initial_equity_by_investment_sector(household_before_investment, sector):
    # Given
    household = household_before_investment
    household.desired_investment_sector = sector
    holder_role = household.roles["citizen"]
    holder_role.get_sector_equity_range.return_value = (100, 500)
    random = household.model.nprandom
    random.uniform.return_value = 300

    # When
    equity = household.calc_initial_equity(sector)

    # Then
    holder_role.get_sector_equity_range.assert_called_with(sector)
    assert equity == 300


@pytest.mark.parametrize("sector", ["FNT", "FT", "B"])
def test_calc_initial_equity_uses_exogenous_equity(household_before_investment, sector):
    # Given
    household = household_before_investment
    household.p.initial_equity = 1000
    holder_role = household.roles["citizen"]
    holder_role.get_sector_equity_range.return_value = None

    # When
    equity = household.calc_initial_equity(sector=sector)

    # Then
    assert equity == 1000


def test_create_company_can_create_non_tradable_firms(household_before_investment):
    # Given
    household = household_before_investment
    role = household.roles["citizen"]
    founders = [Mock() for _ in range(5)]

    # When
    household.create_company(founders, sector="FNT")

    # Then
    role.create_firm.assert_called_once_with(founders, tradable=False)


def test_create_company_can_create_tradable_firms(household_before_investment):
    # Given
    household = household_before_investment
    role = household.roles["citizen"]
    founders = [Mock() for _ in range(5)]

    # When
    household.create_company(founders, sector="FT")

    # Then
    role.create_firm.assert_called_once_with(founders, tradable=True)


def test_create_company_can_create_bank(household_before_investment):
    # Given
    household = household_before_investment
    role = household.roles["citizen"]
    founders = [Mock() for _ in range(5)]

    # When
    household.create_company(founders, sector="B")

    # Then
    role.create_bank.assert_called_once_with(founders)


@pytest.fixture
def household_as_depositor(household_with_roles):
    # Given
    role = Mock()
    household, roles = household_with_roles
    roles["depositor"] = role
    return household, role


def test_make_deposits_with_residual_cash(household_as_depositor):
    # Given
    household, role = household_as_depositor
    household.cash = 500
    household.country = "any"

    # When
    household.make_deposits()

    # Then
    role.make_deposits.assert_called_with(500)


@pytest.fixture
def household_as_investor():
    model = Mock()
    household = Household(model)
    household.equity = 0
    household.desired_equity = 100
    household.roles = {"citizen": Mock()}
    household.choose_investment_sector = Mock(return_value=None)
    household.find_potential_investors = Mock(return_value=[])
    household.calc_initial_equity = Mock(return_value=100)
    household.create_company = Mock()
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
    household.create_company.assert_not_called()
    household.make_deposits.assert_called_with()


def test_invest_equity_when_sufficient_equity(household_as_investor):
    # Given
    household = household_as_investor
    initiator = household.roles["citizen"]
    founders = [Mock(desired_equity=100) for _ in range(2)]
    household.find_potential_investors.return_value = founders
    household.choose_investment_sector.return_value = "any"
    household.calc_initial_equity.return_value = 300

    # When
    household.invest_equity()

    # Then
    household.find_potential_investors.assert_called_with()
    household.calc_initial_equity.assert_called_with("any")
    household.create_company.assert_called_with([initiator] + founders, "any")
    household.make_deposits.assert_called_with()


def test_invest_equity_with_only_sufficient_equity(household_as_investor):
    # Given
    household = household_as_investor
    initiator = household.roles["citizen"]
    founders = [Mock(desired_equity=100) for _ in range(5)]
    household.find_potential_investors.return_value = founders
    household.choose_investment_sector.return_value = "any"
    household.calc_initial_equity.return_value = 300

    # When
    household.invest_equity()

    # Then
    household.find_potential_investors.assert_called_with()
    household.calc_initial_equity.assert_called_with("any")
    household.create_company.assert_called_with([initiator] + founders[:2], "any")
    household.make_deposits.assert_called_with()


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
    household.create_company.assert_not_called()
    household.make_deposits.assert_called_with()


def test_choose_deposit_bank_opens_account_randomly(household_as_depositor):
    # Given
    banks = [Mock() for _ in range(3)]
    household, role = household_as_depositor
    household.model.random.choice.side_effect = lambda x: x[-1]
    role.find_deposit_banks.return_value = banks

    # When
    household.choose_deposit_bank()

    # Then
    role.choose_bank.assert_called_once_with(banks[-1])
