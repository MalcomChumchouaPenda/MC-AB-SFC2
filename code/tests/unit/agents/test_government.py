import pytest
from unittest.mock import Mock, PropertyMock
from model.agents.government import Government

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from model.base import EcoAgent

    # Assert
    assert issubclass(Government, EcoAgent)


@pytest.fixture
def govt():
    # Given
    model = Mock()
    govt = Government(model)
    govt.setup()
    return govt


def test_has_default_space_refs(govt):
    # Assert
    assert govt.country is None


def test_has_default_profits_value(govt):
    # Assert
    assert govt.profits == 0


def test_has_default_reserves_value(govt):
    # Assert
    assert govt.reserves == 0


def test_has_default_bond_supply_value(govt):
    # Assert
    assert govt.bond_supply == 0.0


def test_has_default_flows(govt):
    # Assert
    assert govt.taxes == 0
    assert govt.public_transfers == 0


def test_has_default_choices(govt):
    # Assert
    assert govt.tax_rate == 0
    assert govt.bond_rate == 0
    assert govt.public_spending == 0
    assert govt.desired_public_spending == 0
    assert govt.new_public_debt == 0


def test_has_default_indicators(govt):
    # Assert
    assert govt.gdp == 0
    assert govt.budget_deficit == 0
    assert govt.budget_surplus == 0
    assert govt.prev_public_spending == 0
    assert govt.prev_budget_surplus == 0


def test_has_default_refs(govt):
    # Assert
    assert govt.central_bank is None


# ---------------------------------------------------
# DERIVED STATE TESTS
# ----------------------------------------------------


@pytest.fixture
def govt_with_country():
    model, country = Mock(), Mock()
    govt = Government(model)
    govt.setup()
    govt.country = country
    return govt, country


def test_expose_bonds_total(govt_with_country):
    # Given
    bonds = [{"buyer": object(), "principal": 500}]
    govt, country = govt_with_country
    bond_market = country.union.bond_market
    bond_market.get_issuer_bonds.return_value = bonds

    # Assert
    assert govt.bonds == 500


def test_expose_bond_interests_total(govt_with_country):
    # Given
    bonds = [{"buyer": object(), "interests": 50.0}]
    govt, country = govt_with_country
    bond_market = country.union.bond_market
    bond_market.get_issuer_bonds.return_value = bonds

    # Assert
    assert govt.bond_interests == pytest.approx(50.0)


# ---------------------------------------------------
# PUBLIC TRANSFERS TESTS
# ----------------------------------------------------


@pytest.fixture
def govt_with_spending():
    # Given
    spending = 100
    model = Mock()
    govt = Government(model)
    govt.setup()
    govt.country = "any"
    govt.public_spending = spending
    return govt, spending


def test_pay_public_transfers_to_domestic_households(govt_with_spending):
    # Given
    govt, spending = govt_with_spending
    household = Mock(country="any", cash=0, public_transfers=0)
    govt.model.households = [household]

    # When
    govt.pay_public_transfers()

    # Then
    assert household.cash == spending
    assert household.public_transfers == spending
    assert govt.reserves == -spending
    assert govt.public_transfers == spending


def test_dont_pay_public_transfers_to_foreign_households(govt_with_spending):
    # Given
    govt, _ = govt_with_spending
    household = Mock(country="other", cash=0, public_transfers=0)
    govt.model.households = [household]

    # When
    govt.pay_public_transfers()

    # Then
    assert household.cash == 0
    assert household.public_transfers == 0
    assert govt.reserves == 0
    assert govt.public_transfers == 0


@pytest.fixture
def govt_with_bond_interests(monkeypatch):
    # Given
    model = Mock()
    interests_prop = PropertyMock()
    monkeypatch.setattr(Government, "bond_interests", interests_prop)
    govt = Government(model)
    return govt, interests_prop


def test_calc_budget_balance(govt_with_bond_interests):
    # Given
    govt, bond_interests = govt_with_bond_interests
    govt.taxes = 1000
    govt.public_spending = 700
    bond_interests.return_value = 100

    # When
    balance = govt.calc_budget_balance()

    # Then
    assert balance == 200


def test_calc_and_records_budget_deficit(govt_with_bond_interests):
    # Given
    govt, bond_interests = govt_with_bond_interests
    govt.taxes = 500
    govt.public_spending = 600
    bond_interests.return_value = 100

    # When
    govt.calc_budget_balance()

    # Then
    assert govt.budget_deficit == 200
    assert govt.budget_surplus == 0


def test_calc_and_records_budget_surplus(govt_with_bond_interests):
    # Given
    govt, bond_interests = govt_with_bond_interests
    govt.taxes = 1000
    govt.public_spending = 700
    bond_interests.return_value = 100

    # When
    govt.calc_budget_balance()

    # Then
    assert govt.budget_surplus == 200
    assert govt.budget_deficit == 0


def test_calc_and_records_with_no_deficit_or_surplus(govt_with_bond_interests):
    # Given
    govt, bond_interests = govt_with_bond_interests
    govt.taxes = 800
    govt.public_spending = 700
    bond_interests.return_value = 100

    # When
    govt.calc_budget_balance()

    # Then
    assert govt.budget_deficit == 0
    assert govt.budget_surplus == 0


def test_calc_and_records_desired_public_spending(govt):
    # Given
    goods_market = Mock(average_price=2, average_productivity=3)
    govt.model.goods_markets = {"any": goods_market}
    govt.prev_public_spending = 10
    govt.country = "any"

    # When
    desired = govt.calc_desired_public_spending()

    # Then
    assert desired == 60
    assert govt.desired_public_spending == desired


@pytest.mark.parametrize("tax_rate, expected", [(0.38, 0.40), (0.58, 0.50)])
def test_tax_rate_is_bounded(govt, tax_rate, expected):
    # Given
    govt.tax_rate = tax_rate
    govt.p.tax_min = 0.40
    govt.p.tax_max = 0.50

    # When
    govt.apply_tax_rate_bounds()

    # Then
    assert govt.tax_rate == expected


@pytest.mark.parametrize("spending, expected", [(80, 100), (150, 120)])
def test_public_spending_is_bounded_by_gdp(govt, spending, expected):
    # Given
    govt.public_spending = spending
    govt.gdp = 1000
    govt.p.g_min = 0.10
    govt.p.g_max = 0.12

    # When
    govt.apply_public_spending_bounds()

    # Then
    assert govt.public_spending == expected


@pytest.fixture
def govt_for_policy():
    # Given
    model = Mock()
    model.p.dmax = 0.05
    model.p.delta = 0.10
    govt = Government(model)
    govt.tax_rate = 0.20
    govt.gdp = 1000
    govt.public_spending = 100
    govt.desired_public_spending = 0
    govt.apply_tax_rate_bounds = Mock()
    govt.apply_public_spending_bounds = Mock()
    govt.calc_desired_public_spending = Mock(return_value=0)
    govt.model.random.uniform.return_value = 0.05
    return govt


def test_update_fiscal_policy_with_random_variation(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 100
    govt.desired_public_spending = 80
    random = govt.model.random

    # When
    govt.update_fiscal_policy()

    # Then
    random.uniform.assert_called_with(0, 0.10)


def test_update_fiscal_policy_with_multi_steps(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 100
    govt.desired_public_spending = 80

    # When
    govt.update_fiscal_policy()

    # Then
    govt.calc_desired_public_spending.assert_called_with()
    govt.apply_public_spending_bounds.assert_called_with()
    govt.apply_tax_rate_bounds.assert_called_with()


def test_reduce_spending_and_increase_tax_when_deficit_high(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 100
    govt.calc_desired_public_spending.return_value = 80

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(95)
    assert govt.tax_rate == pytest.approx(0.21)


def test_keep_spending_and_increase_tax_when_deficit_high(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 100
    govt.calc_desired_public_spending.return_value = 120

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(100)
    assert govt.tax_rate == pytest.approx(0.21)


def test_reduce_spending_and_tax_when_deficit_low(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 20
    govt.calc_desired_public_spending.return_value = 80

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(95)
    assert govt.tax_rate == pytest.approx(0.19)


def test_increase_spending_and_keep_tax_when_deficit_low(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 20
    govt.calc_desired_public_spending.return_value = 120

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(105)
    assert govt.tax_rate == pytest.approx(0.20)


@pytest.fixture
def govt_with_bonds(monkeypatch):
    # Given
    model = Mock()
    bonds_prop = PropertyMock()
    monkeypatch.setattr(Government, "bonds", bonds_prop)
    govt = Government(model)
    return govt, bonds_prop


def test_calc_new_debt(govt_with_bonds):
    # Given
    govt, bonds = govt_with_bonds
    govt.budget_deficit = 200
    govt.prev_budget_surplus = 50
    bonds.return_value = 1000

    # When
    new_debt = govt.calc_new_debt()

    # Then
    assert new_debt == 1150
    assert govt.new_public_debt == 1150


def test_calc_new_bonds(govt_with_bonds):
    # Given
    govt, bonds = govt_with_bonds
    govt.new_public_debt = 1150
    bonds.return_value = 1000

    # When
    issuance = govt.calc_new_bonds()

    # Then
    assert issuance == 150


def test_calc_not_new_bonds_with_enough_bonds(govt_with_bonds):
    # Given
    govt, bonds = govt_with_bonds
    govt.new_public_debt = 900
    bonds.return_value = 1000

    # When
    issuance = govt.calc_new_bonds()

    # Then
    assert issuance == 0


@pytest.fixture
def govt_as_bond_supplier():
    # Given
    model = Mock()
    govt = Government(model)
    govt.bond_supply = 0
    govt.calc_new_debt = Mock(return_value=0)
    govt.calc_new_bonds = Mock(return_value=0)
    return govt


def test_issues_bonds(govt_as_bond_supplier):
    # Given
    govt = govt_as_bond_supplier
    govt.bond_supply = 100
    govt.calc_new_bonds.return_value = 500

    # When
    govt.issue_bonds()

    # Then
    assert govt.bond_supply == 600


def test_issues_bonds_with_multi_step(govt_as_bond_supplier):
    # Given
    govt = govt_as_bond_supplier

    # When
    govt.issue_bonds()

    # Then
    govt.calc_new_debt.assert_called_with()
    govt.calc_new_bonds.assert_called_with()


def test_repay_bonds_calc_and_register_bond_rate(govt_with_country):
    # Given
    govt, country = govt_with_country
    bond_market = country.union.bond_market
    bond_market.get_issuer_bonds.return_value = []
    govt.calc_bond_rate = Mock(return_value=0.01)

    # When
    govt.repay_bonds()

    # Then
    assert govt.bond_rate == 0.01


def test_repay_bonds_uses_bond_market(govt_with_country):
    # Given
    buyer = object()
    bonds = [{"buyer": buyer, "principal": 500}]
    govt, country = govt_with_country
    bond_market = country.union.bond_market
    bond_market.get_issuer_bonds.return_value = bonds
    govt.calc_bond_rate = Mock(return_value=0.01)

    # When
    govt.repay_bonds()

    # Then
    bond_market.repay_bonds.assert_called_with(govt, buyer, 500, 5.0)


def test_calc_bond_rate(govt_with_bonds):
    # Given
    govt, bonds = govt_with_bonds
    govt.central_bank = Mock(discount_rate=0.03)
    govt.gdp = 1000
    govt.p.chi = 0.02
    bonds.return_value = 500

    # when
    rate = govt.calc_bond_rate()

    # Then
    assert rate == 0.04


@pytest.fixture
def model_with_deposit_markets():
    # Given
    deposit_market = Mock()
    model = Mock()
    model.deposit_markets = {"any": deposit_market}
    return model, deposit_market


@pytest.fixture
def govt_as_deposit_guarantee(model_with_deposit_markets):
    # Given
    model, deposit_market = model_with_deposit_markets
    govt = Government(model)
    govt.bond_supply = 0
    govt.country = "any"
    govt._defaults = []
    return govt, deposit_market


def test_issue_deposit_guarantee_bonds(govt_as_deposit_guarantee):
    # Given
    govt, deposit_market = govt_as_deposit_guarantee
    govt.bond_supply = 100
    defaults = [Mock(deposits=100) for _ in range(3)]
    deposit_market.get_defaulted_banks.return_value = defaults

    # When
    govt.issue_deposit_guarantee_bonds()

    # Then
    assert govt.bond_supply == 400


def test_issue_deposit_guarantee_bonds_registers_defaults(govt_as_deposit_guarantee):
    # Given
    defaults = [Mock(deposits=100)]
    govt, deposit_market = govt_as_deposit_guarantee
    deposit_market.get_defaulted_banks.return_value = defaults

    # When
    govt.issue_deposit_guarantee_bonds()

    # Then
    assert govt._defaults == defaults


def test_reimburse_deposits(govt_as_deposit_guarantee):
    # Given
    bank = Mock()
    govt, market = govt_as_deposit_guarantee
    govt._defaults = [bank]
    client = Mock()
    market.get_bank_deposits.return_value = [{"client": client}]

    # When
    govt.reimburse_deposits()

    # Then
    market.get_bank_deposits.assert_called_with(bank)
    market.reimburse_deposits.assert_called_with(govt, client, bank)


@pytest.fixture
def govt_with_history():
    # Given
    model = Mock()
    goods_market = Mock(gdp=0)
    govt = Government(model)
    govt.setup()
    govt.country = "any"
    model.goods_markets = {"any": goods_market}
    return govt


def test_update_production_history(govt_with_history):
    # Given
    govt = govt_with_history
    goods_market = govt.model.goods_markets["any"]
    goods_market.gdp = 120

    # When
    govt.update_history()

    # Then
    assert govt.gdp == 120


def test_update_public_spending_history(govt_with_history):
    # Given
    govt = govt_with_history
    govt.public_spending = 200
    govt.prev_public_spending = 150

    # When
    govt.update_history()

    # Then
    assert govt.prev_public_spending == 200


def test_update_budget_history(govt_with_history):
    # Given
    govt = govt_with_history
    govt.budget_surplus = 100
    govt.prev_budget_surplus = 0

    # When
    govt.update_history()

    # Then
    assert govt.prev_budget_surplus == 100
