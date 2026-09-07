import pytest
from unittest.mock import Mock
from model.agents.central_bank import CentralBank

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from model.base import EcoAgent

    # Assert
    assert issubclass(CentralBank, EcoAgent)


@pytest.fixture
def cb_before_setup():
    # Given
    model = Mock()
    cb = CentralBank(model)
    return cb


def test_has_default_previous_discount_rate(cb_before_setup):
    # Given
    cb = cb_before_setup

    # When
    cb.setup()

    # Then
    assert cb.prev_discount_rate == 0


def test_has_default_discount_rate(cb_before_setup):
    # Given
    cb = cb_before_setup

    # When
    cb.setup()

    # Then
    assert cb.discount_rate == 0


# ---------------------------------------------------
# BONDS PURCHASES
# ----------------------------------------------------


@pytest.fixture
def cb_as_bond_buyer(cb_before_setup):
    # Given
    role = Mock()
    cb = cb_before_setup
    cb.roles = {"bond_buyer": role}
    cb.country = 1
    return cb, role


def test_buy_all_domestic_remaining_bonds(cb_as_bond_buyer):
    # Given
    issuer = Mock(country=1, bond_number=5)
    cb, role = cb_as_bond_buyer
    role.find_issuers.return_value = [issuer]

    # When
    cb.buy_remaining_bonds()

    # Then
    role.buy_bonds.assert_called_with(issuer, 5)


def test_dont_buy_foreign_bonds(cb_as_bond_buyer):
    # Given
    issuer = Mock(country=2, bond_number=5)
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
def cb_as_authority(cb_before_setup):
    # Given
    role = Mock()
    cb = cb_before_setup
    cb.account = Mock(stocks={}, flows={})
    cb.roles = {"monetary_authority": role}
    return cb, role


def test_calc_discount_rate(cb_as_authority):
    # Given
    cb, _ = cb_as_authority
    cb.average_inflation = 0.04
    cb.prev_discount_rate = 0.03
    cb.p.long_run_rate = 0.02
    cb.p.xi = 0.5
    cb.p.xi_deltap = 1.5
    cb.p.inflation_target = 0.02

    # When
    discount_rate = cb.calc_discount_rate()

    # Then
    assert discount_rate == pytest.approx(0.04)


def test_determine_discount_rate(cb_as_authority):
    # Given
    cb, role = cb_as_authority
    cb.prev_discount_rate = 0.0
    cb.discount_rate = 0.0
    cb.calc_discount_rate = Mock(return_value=0.02)
    role.get_average_inflation.return_value = 0.05

    # When
    cb.determine_discount_rate()

    # Then
    assert cb.discount_rate == 0.02


def test_determine_discount_rate_changes_lag_values(cb_as_authority):
    # Given
    cb, role = cb_as_authority
    cb.prev_discount_rate = 0.01
    cb.discount_rate = 0.02
    cb.calc_discount_rate = Mock(return_value=0.03)
    role.get_average_inflation.return_value = 0.0

    # When
    cb.determine_discount_rate()

    # Then
    assert cb.prev_discount_rate == 0.02
    assert cb.discount_rate == 0.03


def test_implement_discount_rate(cb_as_authority):
    # Given
    cb, role = cb_as_authority
    cb.prev_discount_rate = 0.0
    cb.discount_rate = 0.0
    role.get_union_discount_rate.return_value = 0.05

    # When
    cb.implement_discount_rate()

    # Then
    assert cb.discount_rate == 0.05


def test_implement_discount_rate_changes_lag_values(cb_as_authority):
    # Given
    cb, role = cb_as_authority
    cb.prev_discount_rate = 0.01
    cb.discount_rate = 0.02
    role.get_union_discount_rate.return_value = 0.03

    # When
    cb.implement_discount_rate()

    # Then
    assert cb.prev_discount_rate == 0.02
    assert cb.discount_rate == 0.03


# ---------------------------------------------------
# PROFIT TRANSFER
# ----------------------------------------------------


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
