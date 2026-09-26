import pytest
from unittest.mock import Mock
from model.roles.policy_maker import PolicyMaker

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.base import EcoRole

    # When
    is_derived = issubclass(PolicyMaker, EcoRole)

    # Then
    assert is_derived


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return PolicyMaker(agent, env)


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_get_average_inflation_from_env(role):
    # Given
    env = role.env
    env.average_inflation = 0.03

    # When
    perceived = role.get_average_inflation()

    # Then
    assert perceived == 0.03


def test_get_discount_rate_from_env(role):
    # Given
    env = role.env
    env.discount_rate = 0.03

    # When
    perceived = role.get_discount_rate()

    # Then
    assert perceived == 0.03


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------


def test_set_discount_rate_into_env(role):
    # Given
    env = role.env
    env.discount_rate = 0.0

    # When
    role.set_discount_rate(0.02)

    # Then
    assert env.discount_rate == 0.02
