import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import DepositHolderRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(DepositHolderRole, EcoRole)


@pytest.fixture
def deposit_holder():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return DepositHolderRole(agent, space)


def test_has_deposit_bank_reference(deposit_holder):
    # Assert
    assert deposit_holder.deposit_bank is None


def test_exposes_deposits(deposit_holder):
    # Given
    agent = deposit_holder.agent
    agent.deposits = 100

    # Assert
    assert deposit_holder.deposits == 100


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_get_deposit_rate(deposit_holder):
    # Given
    deposit_bank = Mock()
    deposit_bank.deposit_rate = 0.02
    deposit_holder.deposit_bank = deposit_bank

    # When
    deposit_rate = deposit_holder.get_deposit_rate()

    # Then
    assert deposit_rate == 0.02


def test_make_deposits(deposit_holder):
    # Given
    deposit_bank = Mock()
    deposit_holder.deposit_bank = deposit_bank
    market = deposit_holder.space

    # When
    deposit_holder.make_deposits(300)

    # Then
    market.make_deposits.assert_called_with(deposit_holder, deposit_bank, 300)


def test_make_no_deposits_if_no_bank(deposit_holder):
    # Given
    deposit_holder.deposit_bank = None
    market = deposit_holder.space

    # When
    deposit_holder.make_deposits(300)

    # Then
    market.make_deposits.assert_not_called()
