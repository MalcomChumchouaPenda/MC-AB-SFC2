import pytest
from unittest.mock import Mock
from model.roles.depositor import Depositor

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(Depositor, EcoRole)


@pytest.fixture
def depositor_before_setup():
    # Given
    model = Mock()
    depositor = Depositor(model)
    return depositor


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def depositor_with_space(depositor_before_setup):
    # Given
    space = Mock()
    depositor = depositor_before_setup
    depositor.space = space
    return depositor, space


def test_find_deposit_banks_from_space(depositor_with_space):
    # Given
    depositor, space = depositor_with_space

    # When
    found = depositor.find_deposit_banks()

    # Then
    space.find_deposit_banks.assert_called_with()
    assert found == space.find_deposit_banks.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_make_deposits_into_space(depositor_with_space):
    # Given
    depositor, space = depositor_with_space

    # When
    depositor.make_deposits(200)

    # Then
    space.make_deposits.assert_called_with(depositor, 200)


def test_withdraw_deposits_into_space(depositor_with_space):
    # Given
    depositor, space = depositor_with_space

    # When
    depositor.withdraw_deposits(200)

    # Then
    space.withdraw_deposits.assert_called_with(depositor, 200)
    

def test_choose_bank_into_space(depositor_with_space):
    # Given
    depositor, space = depositor_with_space
    depositor.deposit_bank = None
    deposit_bank = Mock()

    # When
    depositor.choose_bank(deposit_bank)

    # Then
    space.link_depositor_to_bank.assert_called_with(depositor, deposit_bank, 0)


def test_choose_bank_with_initial_amount(depositor_with_space):
    # Given
    depositor, space = depositor_with_space
    depositor.deposit_bank = None
    deposit_bank = Mock()

    # When
    depositor.choose_bank(deposit_bank, amount=100)

    # Then
    space.link_depositor_to_bank.assert_called_with(depositor, deposit_bank, 100)
    

def test_choose_bank_to_switch_bank(depositor_with_space):
    # Given
    old_deposit_bank = Mock()
    new_deposit_bank = Mock()
    depositor, space = depositor_with_space
    depositor.deposit_bank = old_deposit_bank

    # When
    depositor.choose_bank(new_deposit_bank)

    # Then
    space.unlink_depositor_with_bank.assert_called_with(depositor)
    space.link_depositor_to_bank.assert_called_with(depositor, new_deposit_bank, 0)

