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
def hh_before_setup():
    # Given
    model = Mock()
    household = Household(model)
    return household


def test_has_default_labor_supply(hh_before_setup):
    # Given
    household = hh_before_setup

    # When
    household.setup()

    # Then
    assert household.labor_supply == 1.0


def test_has_default_preference(hh_before_setup):
    # Given
    household = hh_before_setup

    # When
    household.setup()

    # Then
    assert household.preference == 0


def test_has_default_reservation_wage(hh_before_setup):
    # Given
    household = hh_before_setup

    # When
    household.setup()

    # Then
    assert household.reservation_wage == 0


def test_has_default_expected_consumption(hh_before_setup):
    # Given
    household = hh_before_setup

    # When
    household.setup()

    # Then
    assert household.expected_consumption == 0


def test_has_default_desired_consumption(hh_before_setup):
    # Given
    household = hh_before_setup

    # When
    household.setup()

    # Then
    assert household.desired_consumption == 0


def test_has_default_desired_equity(hh_before_setup):
    # Given
    household = hh_before_setup

    # When
    household.setup()

    # Then
    assert household.desired_equity == 0


def test_has_default_desired_deposits(hh_before_setup):
    # Given
    household = hh_before_setup

    # When
    household.setup()

    # Then
    assert household.desired_deposits == 0


def test_has_default_desired_investment_sector(hh_before_setup):
    # Given
    household = hh_before_setup

    # When
    household.setup()

    # Then
    assert household.desired_investment_sector is None


def test_has_default_net_worth(hh_before_setup):
    # Given
    household = hh_before_setup

    # When
    household.setup()

    # Then
    assert household.net_worth == 0


def test_has_default_incomes(hh_before_setup):
    # Given
    household = hh_before_setup

    # When
    household.setup()

    # Then
    assert household.income == 0
    assert household.disposable_income == 0


# ---------------------------------------------------
# JOB SEARCH TESTS
# ----------------------------------------------------


@pytest.fixture
def hh_with_roles_and_account(hh_before_setup):
    # Given
    roles = {}
    account = Mock(stocks={}, flows={})
    household = hh_before_setup
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
# WAGE REVISION TESTS
# ----------------------------------------------------


def test_calc_revision_probability(hh_with_roles_and_account):
    # Given
    role = Mock()
    role.get_unemployment.return_value = 0.1
    household, roles, _ = hh_with_roles_and_account
    household.p.upsilon = 1.0
    household.p.upsilon_h = 0.9
    roles["worker"] = role

    # When
    result = household.calc_revision_probability()

    # Then
    assert result == 0.9 * math.exp(-1.0 * 0.1)


@pytest.fixture
def fully_employed_before(hh_with_roles_and_account):
    # Given
    household, *_ = hh_with_roles_and_account
    household.p.delta = 0.9
    household.prev_labor_sold = 1.0
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
def part_employed_before(hh_with_roles_and_account):
    # Given
    household, *_ = hh_with_roles_and_account
    household.p.delta = 0.9
    household.prev_labor_sold = 0.5
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
    household.account.flows["wages"] = 110
    household.account.flows["dep_interests"] = 20
    household.account.flows["dividends"] = 30

    # When
    income = household.calc_income()

    # Then
    assert income == 160


def test_calc_disposable_income(hh_as_taxpayer):
    # Given
    household, _ = hh_as_taxpayer
    household.income = 200
    household.account.flows["public_transfers"] = 50

    # When
    disposable_income = household.calc_disposable_income()

    # Then
    assert disposable_income == 210


def test_pay_taxes_transfers_cash(hh_as_taxpayer):
    # Given
    household, role = hh_as_taxpayer
    household.calc_income = Mock(return_value=100)
    household.calc_disposable_income = Mock(return_value=110)

    # When
    household.pay_taxes()

    # Then
    role.pay_taxes.assert_called_with(20)


def test_pay_taxes_updates_indicators(hh_as_taxpayer):
    # Given
    household, _ = hh_as_taxpayer
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


def test_calc_consumption_updates_choice(hh_with_roles_and_account):
    # Given
    household, _, account = hh_with_roles_and_account
    household.p.cy = 0.8
    household.p.cd = 0.1
    household.disposable_income = 1000
    account.stocks["deposits"] = 500

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
    account.stocks["cash"] = 1000
    return household, role, account


def test_calc_supplier_score_with_salop_formula(hh_as_specific_consumer):
    # Given
    household, *_ = hh_as_specific_consumer
    household.p.beta = 1
    household.preference = 0
    supplier = Mock(variety=0.5, price=10)

    # When
    score = household.calc_supplier_score(supplier, average_price=20)

    # Then
    expected_distance = math.sin(0.5 / 2)
    assert score == (1 / expected_distance) * (20 / 10)


def test_rank_suppliers_using_supplier_score(hh_as_specific_consumer):
    # Given
    method = lambda supplier, average_price: average_price / supplier.price
    household, *_ = hh_as_specific_consumer
    household.calc_supplier_score = method
    suppliers = [Mock(price=i, variety=1) for i in range(1, 3)]

    # When
    ranked = household.rank_suppliers(suppliers, average_price=10)

    # Then
    assert ranked[0].price == 1
    assert ranked[1].price == 2


def test_consume_good_with_found_suppliers(hh_as_specific_consumer):
    # Given
    found = [Mock(price=5, inventories=10) for _ in range(5)]
    household, role, _ = hh_as_specific_consumer
    household.p.psi = 5
    household.rank_suppliers = Mock(return_value=found)
    role.find_suppliers.return_value = found
    role.get_average_price.return_value = 20

    # When
    household.consume_good(role, 100)

    # Then
    role.find_suppliers.assert_called_with(5)
    household.rank_suppliers.assert_any_call(found, average_price=20)


def test_consume_good_with_ranked_suppliers(hh_as_specific_consumer):
    # Given
    ranked = [Mock(price=5, inventories=10) for _ in range(2)]
    household, role, _ = hh_as_specific_consumer
    household.rank_suppliers = Mock(return_value=ranked)

    # When
    household.consume_good(role, 100)

    # Then
    role.buy_goods.assert_any_call(ranked[0], 10)
    role.buy_goods.assert_any_call(ranked[1], 10)
    assert role.buy_goods.call_count == 2


def test_consume_good_with_desired_consumption(hh_as_specific_consumer):
    # Given
    ranked = [Mock(price=5, inventories=10) for _ in range(2)]
    household, role, _ = hh_as_specific_consumer
    household.rank_suppliers = Mock(return_value=ranked)

    # When
    household.consume_good(role, 50)

    # Then
    role.buy_goods.assert_any_call(ranked[0], 10)
    assert role.buy_goods.call_count == 1


def test_consume_good_with_supply_constraints(hh_as_specific_consumer):
    # Given
    ranked = [Mock(price=5, inventories=5) for _ in range(2)]
    household, role, _ = hh_as_specific_consumer
    household.rank_suppliers = Mock(return_value=ranked)

    # When
    household.consume_good(role, 100)

    # Then
    role.buy_goods.assert_any_call(ranked[0], 5)
    role.buy_goods.assert_any_call(ranked[1], 5)
    assert role.buy_goods.call_count == 2


def test_consume_good_with_monetary_constraints(hh_as_specific_consumer):
    # Given
    ranked = [Mock(price=5, inventories=10) for _ in range(2)]
    household, role, account = hh_as_specific_consumer
    household.rank_suppliers = Mock(return_value=ranked)
    account.stocks["cash"] = 50

    # When
    household.consume_good(role, 100)

    # Then
    role.buy_goods.assert_any_call(ranked[0], 10)
    assert role.buy_goods.call_count == 1


@pytest.fixture
def hh_as_general_consumer(hh_with_roles_and_account):
    # Given
    household, roles, account = hh_with_roles_and_account
    household.consume_good = Mock()
    roles["depositor"] = Mock()
    roles["trad_consumer"] = Mock()
    roles["non_trad_consumer"] = Mock()
    account.stocks["cash"] = 0
    account.stocks["deposits"] = 0
    return household, roles, account


def test_consume_each_good_type(hh_as_general_consumer):
    # Given
    household, roles, _ = hh_as_general_consumer
    household.p.cT = 0.6
    household.desired_consumption = 100
    # When
    household.consume()

    # Then
    household.consume_good.assert_any_call(roles["trad_consumer"], 60.0)
    household.consume_good.assert_any_call(roles["non_trad_consumer"], 40.0)


def test_consume_randomizes_entry_order(hh_as_general_consumer):
    # Given
    household, roles, _ = hh_as_general_consumer
    household.p.cT = 0.6
    household.desired_consumption = 100
    random = household.model.random
    entry_order = [
        (roles["trad_consumer"], 60.0),
        (roles["non_trad_consumer"], 40.0),
    ]

    # When
    household.consume()

    # Then
    random.shuffle.assert_called_with(entry_order)


def test_consume_with_insufficient_cash(hh_as_general_consumer):
    # Given
    household, roles, account = hh_as_general_consumer
    household.p.cT = 0.6
    household.desired_consumption = 100
    account.stocks["deposits"] = 100
    account.stocks["cash"] = 50
    role = roles["depositor"]

    # When
    household.consume()

    # Then
    role.withdraw_deposits.assert_called_with(50)
    assert household.consume_good.call_count == 2


def test_consume_with_insufficient_deposits(hh_as_general_consumer):
    # Given
    household, roles, account = hh_as_general_consumer
    household.p.cT = 0.6
    household.desired_consumption = 100
    account.stocks["deposits"] = 25
    account.stocks["cash"] = 50
    role = roles["depositor"]

    # When
    household.consume()

    # Then
    role.withdraw_deposits.assert_called_with(25)
    assert household.consume_good.call_count == 2


# ---------------------------------------------------
# PORTFOLIO ALLOCATION TESTS
# ----------------------------------------------------


@pytest.fixture
def hh_before_allocation(hh_with_roles_and_account):
    # Given
    household, roles, _ = hh_with_roles_and_account
    roles["citizen"] = Mock()
    roles["depositor"] = Mock()
    return household


def test_calc_net_worth(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account.stocks["deposits"] = 200
    household.account.stocks["equities"] = 300
    household.account.stocks["cash"] = 500

    # When
    household.calc_net_worth()

    # Then
    assert household.net_worth == 1000


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
    household.account.flows["dividends"] = 10
    household.account.stocks["equities"] = 100
    household.p.lambda_ = 0.6
    roles = household.roles
    roles["citizen"].get_prob_failure.return_value = 0.10
    roles["depositor"].get_deposit_rate.return_value = 0.05
    expected = 0.6 * math.exp(((10 * (1 - 0.10)) / 100) - 0.05)

    # When
    lp = household.calc_liquidity_preference()

    # Then
    assert lp == pytest.approx(expected)


def test_calc_liquidity_pref_when_equity_is_less_profitable(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account.flows["dividends"] = 2
    household.account.stocks["equities"] = 100
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
    household.account.flows["dividends"] = 0
    household.account.stocks["equities"] = 0
    household.p.lambda_ = 0.8
    roles = household.roles
    roles["citizen"].get_prob_failure.return_value = 0.10
    roles["depositor"].get_deposit_rate.return_value = 0.05

    # When
    lp = household.calc_liquidity_preference()

    # Then
    assert lp == 0.8


def test_choose_portfolio_allocation_calc_net_worth(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account.stocks["equities"] = 80
    household.calc_liquidity_preference = Mock(return_value=0.80)
    household.calc_expected_net_worth = Mock(return_value=100)
    household.calc_net_worth = Mock()

    # When
    household.choose_portfolio_allocation()

    # Then
    household.calc_net_worth.assert_called_once_with()


def test_choose_portfolio_allocation_updates_desired_assets(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account.stocks["equities"] = 20
    household.calc_liquidity_preference = Mock(return_value=0.40)
    household.calc_expected_net_worth = Mock(return_value=100)
    household.calc_net_worth = Mock()

    # When
    household.choose_portfolio_allocation()

    # Then
    assert household.desired_equity == 60
    assert household.desired_deposits == 60


def test_choose_portfolio_allocation_preserves_existing_equity(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account.stocks["equities"] = 80
    household.calc_liquidity_preference = Mock(return_value=0.80)
    household.calc_expected_net_worth = Mock(return_value=100)
    household.calc_net_worth = Mock()

    # When
    household.choose_portfolio_allocation()

    # Then
    assert household.desired_equity == 80


def test_choose_portfolio_allocation_updates_citizen_role(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account.stocks["equities"] = 80
    household.calc_liquidity_preference = Mock(return_value=0.80)
    household.calc_expected_net_worth = Mock(return_value=100)
    household.calc_net_worth = Mock()
    role = household.roles["citizen"]

    # When
    household.choose_portfolio_allocation()

    # Then
    assert role.resid_equity == 80


FakeFirm = Mock()
FakeBank = Mock()


@pytest.fixture
def hh_before_investment(monkeypatch):
    # Given
    monkeypatch.setattr("model.agents.household.Firm", FakeFirm)
    monkeypatch.setattr("model.agents.household.Bank", FakeBank)
    model = Mock()
    model.p.cT = 0.6
    model.p.eta = 0.3
    household = Household(model)
    household.roles = {"citizen": Mock()}
    return household


def test_find_potential_equity_investors(hh_before_investment):
    # Given
    investors = [Mock(), Mock()]
    household = hh_before_investment
    role = household.roles["citizen"]
    role.find_investors.return_value = investors

    # When
    result = household.find_potential_investors()

    # Then
    assert result == investors


@pytest.mark.parametrize("ratio1, ratio2", [(0.2, 0.5), (0.5, 0.2)])
def test_choose_bank_as_investment_sector(hh_before_investment, ratio1, ratio2):
    # Given
    household = hh_before_investment
    role = household.roles["citizen"]
    role.get_bank_number_ratio.return_value = ratio1
    role.get_bank_equity_ratio.return_value = ratio2

    # When
    sector = household.choose_investment_sector()

    # Then
    assert sector == "B"
    assert household.desired_investment_sector == sector


def test_choose_firm_as_investment_sector(hh_before_investment):
    # Given
    household = hh_before_investment
    role = household.roles["citizen"]
    role.get_bank_number_ratio.return_value = 0.6
    role.get_bank_equity_ratio.return_value = 0.6
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
def test_calc_initial_equity_by_investment_sector(hh_before_investment, sector):
    # Given
    household = hh_before_investment
    household.desired_investment_sector = sector
    role = household.roles["citizen"]
    role.get_sector_equity_range.return_value = (100, 500)
    random = household.model.nprandom
    random.uniform.return_value = 300

    # When
    equity = household.calc_initial_equity(sector)

    # Then
    role.get_sector_equity_range.assert_called_with(sector)
    assert equity == 300


@pytest.mark.parametrize("sector", ["FNT", "FT", "B"])
def test_calc_initial_equity_uses_exogenous_equity(hh_before_investment, sector):
    # Given
    household = hh_before_investment
    household.p.initial_equity = 1000
    role = household.roles["citizen"]
    role.get_sector_equity_range.return_value = None

    # When
    equity = household.calc_initial_equity(sector=sector)

    # Then
    assert equity == 1000


def test_create_company_can_create_non_tradable_firms(hh_before_investment):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household = hh_before_investment
    role = household.roles["citizen"]
    shares = [Mock() for _ in range(5)]

    # When
    household.create_company(shares, sector="FNT")

    # Then
    FakeFirm.assert_called_with(household.model)
    role.create_firm.assert_called_once_with(firm, shares, tradable=False)


def test_create_company_can_create_tradable_firms(hh_before_investment):
    # Given
    firm = Mock()
    FakeFirm.return_value = firm
    household = hh_before_investment
    role = household.roles["citizen"]
    shares = [Mock() for _ in range(5)]

    # When
    household.create_company(shares, sector="FT")

    # Then
    FakeFirm.assert_called_with(household.model)
    role.create_firm.assert_called_once_with(firm, shares, tradable=True)


def test_create_company_can_create_bank(hh_before_investment):
    # Given
    bank = Mock()
    FakeBank.return_value = bank
    household = hh_before_investment
    role = household.roles["citizen"]
    shares = [Mock() for _ in range(5)]

    # When
    household.create_company(shares, sector="B")

    # Then
    FakeBank.assert_called_with(household.model)
    role.create_bank.assert_called_once_with(bank, shares)


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
    household.account.stocks["cash"] = 500

    # When
    household.make_deposits()

    # Then
    role.make_deposits.assert_called_with(500)


@pytest.fixture
def hh_as_investor(hh_before_allocation):
    # Given
    household = hh_before_allocation
    household.account.stocks["equities"] = 0
    household.desired_equity = 100
    household.roles = {"citizen": Mock(resid_equity=100)}
    household.choose_investment_sector = Mock(return_value=None)
    household.find_potential_investors = Mock(return_value=[])
    household.calc_initial_equity = Mock(return_value=100)
    household.create_company = Mock()
    household.make_deposits = Mock()
    household.withdraw_deposits = Mock()
    return household


def test_invest_equity_does_nothing_without_desire(hh_as_investor):
    # Given
    household = hh_as_investor
    household.desired_equity = 0

    # When
    household.invest_equity()

    # Then
    household.choose_investment_sector.assert_not_called()
    household.find_potential_investors.assert_not_called()
    household.calc_initial_equity.assert_not_called()
    household.create_company.assert_not_called()
    household.make_deposits.assert_called_with()


def test_invest_equity_when_sufficient_equity(hh_as_investor):
    # Given
    household = hh_as_investor
    initiator = household.roles["citizen"]
    founders = [Mock(resid_equity=100) for _ in range(2)]
    shares = [{"founder": o, "amount": o.resid_equity} for o in [initiator] + founders]
    household.find_potential_investors.return_value = founders
    household.choose_investment_sector.return_value = "any"
    household.calc_initial_equity.return_value = 300

    # When
    household.invest_equity()

    # Then
    household.find_potential_investors.assert_called_with()
    household.calc_initial_equity.assert_called_with("any")
    household.create_company.assert_called_with(shares, "any")
    household.make_deposits.assert_called_with()


def test_invest_equity_with_only_sufficient_equity(hh_as_investor):
    # Given
    household = hh_as_investor
    initiator = household.roles["citizen"]
    founders = [Mock(resid_equity=100) for _ in range(5)]
    shares = [
        {"founder": o, "amount": o.resid_equity} for o in [initiator] + founders[:2]
    ]
    household.find_potential_investors.return_value = founders
    household.choose_investment_sector.return_value = "any"
    household.calc_initial_equity.return_value = 300

    # When
    household.invest_equity()

    # Then
    household.find_potential_investors.assert_called_with()
    household.calc_initial_equity.assert_called_with("any")
    household.create_company.assert_called_with(shares, "any")
    household.make_deposits.assert_called_with()


def test_invest_equity_does_nothing_when_insufficient_equity(hh_as_investor):
    # Given
    household = hh_as_investor
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


def test_choose_deposit_bank_opens_account_randomly(hh_as_depositor):
    # Given
    banks = [Mock() for _ in range(3)]
    household, role = hh_as_depositor
    household.model.random.choice.side_effect = lambda x: x[-1]
    role.find_deposit_banks.return_value = banks

    # When
    household.choose_deposit_bank()

    # Then
    role.choose_bank.assert_called_once_with(banks[-1])
