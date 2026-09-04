import pytest
from unittest.mock import Mock
from model.roles.deposit_guarantee import DepositGuarantee

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(DepositGuarantee, EcoRole)


@pytest.fixture
def guarantee_before_setup():
    # Given
    model = Mock()
    guarantee = DepositGuarantee(model)
    return guarantee


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def guarantee_with_space(guarantee_before_setup):
    # Given
    space = Mock()
    guarantee = guarantee_before_setup
    guarantee.space = space
    return guarantee, space


def test_find_defaulted_banks_from_space(guarantee_with_space):
    # Given
    guarantee, space = guarantee_with_space

    # When
    found = guarantee.find_defaulted_banks()

    # Then
    space.find_defaulted_banks.assert_called_with()
    assert found == space.find_defaulted_banks.return_value


def test_find_deposit_accounts_from_space(guarantee_with_space):
    # Given
    guarantee, space = guarantee_with_space
    bank = Mock()

    # When
    found = guarantee.find_deposit_accounts(bank)

    # Then
    space.find_deposit_accounts.assert_called_with(bank)
    assert found == space.find_deposit_accounts.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_reimburse_deposits_into_space(guarantee_with_space):
    # Given
    guarantee, space = guarantee_with_space
    depositor = Mock()

    # When
    guarantee.reimburse_deposits(depositor, 200)

    # Then
    space.reimburse_deposits.assert_called_with(guarantee, depositor, 200)
