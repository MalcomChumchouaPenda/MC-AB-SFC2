import pytest
from unittest.mock import Mock
from model.agents.central_bank import CentralBank

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_agent():
    # Given
    from model.base import EcoAgent

    # When
    is_derived = issubclass(CentralBank, EcoAgent)

    # Then
    assert is_derived


# ---------------------------------------------------
# DEFAULT STATE
# ----------------------------------------------------
@pytest.fixture
def cb():
    # Given
    model = Mock()
    cb = CentralBank(model)
    return cb


def test_has_default_previous_discount_rate(cb):
    # Assert
    assert cb.prev_discount_rate == 0


# ---------------------------------------------------
# BONDS PURCHASES
# ----------------------------------------------------


@pytest.fixture
def cb_as_bond_buyer(cb):
    # Given
    role = Mock()
    cb.roles = {"bond_buyer": role}
    cb.country_id = 1
    return cb, role


def test_buy_all_domestic_remaining_bonds(cb_as_bond_buyer):
    # Given
    issuer = Mock(country_id=1, bond_number=5)
    cb, role = cb_as_bond_buyer
    role.find_issuers.return_value = [issuer]

    # When
    cb.buy_remaining_bonds()

    # Then
    role.buy_bonds.assert_called_with(issuer, 5)


def test_dont_buy_foreign_bonds(cb_as_bond_buyer):
    # Given
    issuer = Mock(country_id=2, bond_number=5)
    cb, role = cb_as_bond_buyer
    role.find_issuers.return_value = [issuer]

    # When
    cb.buy_remaining_bonds()

    # Then
    role.buy_bonds.assert_not_called()


# ---------------------------------------------------
# MONETARY POLICY
# ----------------------------------------------------


@pytest.fixture
def cb_with_roles_and_account(cb):
    # Given
    roles = {}
    account = Mock(stocks={}, flows={})
    cb.account = account
    cb.roles = roles
    return cb, roles, account


@pytest.fixture
def cb_as_policy_maker(cb_with_roles_and_account):
    # Given
    role = Mock()
    cb, roles, _ = cb_with_roles_and_account
    roles["monetary_authority"] = Mock()
    roles["policy_maker"] = role
    return cb, role


def test_calc_discount_rate(cb_as_policy_maker):
    # Given
    cb, role = cb_as_policy_maker
    cb.prev_discount_rate = 0.03
    cb.p.long_run_rate = 0.02
    cb.p.xi = 0.5
    cb.p.xi_deltap = 1.5
    cb.p.inflation_target = 0.02
    role.get_average_inflation.return_value = 0.04

    # When
    discount_rate = cb.calc_discount_rate()

    # Then
    assert discount_rate == pytest.approx(0.04)


def test_determine_discount_rate(cb_as_policy_maker):
    # Given
    cb, role = cb_as_policy_maker
    cb.prev_discount_rate = 0.0
    cb.calc_discount_rate = Mock(return_value=0.02)
    role.get_discount_rate.return_value = 0.0

    # When
    cb.determine_discount_rate()

    # Then
    role.set_discount_rate.assert_called_with(0.02)


def test_determine_discount_rate_changes_lag_values(cb_as_policy_maker):
    # Given
    cb, role = cb_as_policy_maker
    cb.prev_discount_rate = 0.01
    cb.calc_discount_rate = Mock(return_value=0.03)
    role.get_discount_rate.return_value = 0.02

    # When
    cb.determine_discount_rate()

    # Then
    assert cb.prev_discount_rate == 0.02


def test_implement_discount_rate(cb_as_policy_maker):
    # Given
    cb, maker_role = cb_as_policy_maker
    cb.prev_discount_rate = 0.0
    auth_role = cb.roles["monetary_authority"]
    maker_role.get_discount_rate.return_value = 0.05

    # When
    cb.implement_discount_rate()

    # Then
    assert auth_role.discount_rate == 0.05


def test_implement_discount_rate_changes_lag_values(cb_as_policy_maker):
    # Given
    cb, role = cb_as_policy_maker
    cb.prev_discount_rate = 0.01
    role.get_discount_rate.return_value = 0.02

    # When
    cb.implement_discount_rate()

    # Then
    assert cb.prev_discount_rate == 0.02


# ---------------------------------------------------
# PROFIT TRANSFER
# ----------------------------------------------------


@pytest.fixture
def cb_as_authority(cb_with_roles_and_account):
    # Given
    role = Mock()
    cb, roles, _ = cb_with_roles_and_account
    roles["monetary_authority"] = role
    return cb, role


def test_calc_profit(cb_as_authority):
    # Given
    cb, _ = cb_as_authority
    cb.account.flows["bond_interests"] = 100
    cb.account.flows["adv_interests"] = 40
    cb.account.flows["cash_interests"] = 20

    # When
    profit = cb.calc_profit()

    # Then
    assert profit == 120


def test_transfer_profit_to_government(cb_as_authority):
    # Given
    cb, role = cb_as_authority
    cb.calc_profit = Mock(return_value=100)

    # When
    cb.transfer_profit()

    # Then
    role.transfer_profit.assert_called_with(100)
