import pytest
from unittest.mock import Mock
from model.roles.deposit_bank import DepositBank

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # Then
    assert issubclass(DepositBank, EcoRole)


def test_initializes_defaulted():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = DepositBank(agent, env)

    # Then
    assert role.defaulted is False


def test_get_deposit_rate_from_env(role):
    # Given
    env = role.env
    env.deposit_rate = 0.01

    # When
    perceived = role.get_deposit_rate()

    # Then
    assert perceived == 0.01


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def agent():
    # Given
    return Mock()


@pytest.fixture
def env():
    # Given
    return Mock()



@pytest.fixture
def role(agent, env):
    # Given
    return DepositBank(agent, env)


def test_find_deposits_from_env(role):
    # Given
    env = role.env

    # When
    found = role.find_deposits()

    # Then
    env.links.assert_called_with(role)
    assert found == env.links.return_value


def test_find_depositor_returns_roles_from_env(role):
    # Given
    roles = {i: Mock() for i in range(5)}
    env = role.env
    env.roles = roles

    # When
    found = role.find_depositor(1)

    # Then
    assert found == roles[1]


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_pay_interests_into_env(role):
    # Given
    env = role.env
    depositor = Mock()

    # When
    role.pay_interests(depositor, 200)

    # Then
    env.pay_interests.assert_called_with(role, depositor, 200)


def test_make_deposits_call_join_deposit_bank_from_env(role):
    # Given
    env = role.env
    depositor = Mock()

    # When
    role.make_deposits(depositor, 200)

    # Then
    env.join_deposit_bank.assert_called_with(depositor, role, 200)
