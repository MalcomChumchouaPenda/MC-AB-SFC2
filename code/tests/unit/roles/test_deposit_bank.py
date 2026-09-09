import pytest
from unittest.mock import Mock
from model.roles.deposit_bank import DepositBank

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(DepositBank, EcoRole)


@pytest.fixture
def role_before_setup():
    # Given
    model = Mock()
    role = DepositBank(model)
    return role


def test_has_defaulted(role_before_setup):
    # Given
    role = role_before_setup

    # When
    role.setup()

    # Then
    assert role.defaulted is False


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def role_with_space(role_before_setup):
    # Given
    space = Mock()
    role = role_before_setup
    role.space = space
    return role, space


def test_find_deposit_accounts_from_space(role_with_space):
    # Given
    role, space = role_with_space

    # When
    found = role.find_deposit_accounts()

    # Then
    space.find_deposit_accounts.assert_called_with(role)
    assert found == space.find_deposit_accounts.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_pay_interests_into_space(role_with_space):
    # Given
    role, space = role_with_space
    depositor = Mock()

    # When
    role.pay_interests(depositor, 200)

    # Then
    space.pay_interests.assert_called_with(role, depositor, 200)
