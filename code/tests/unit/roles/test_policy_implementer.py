import pytest
from unittest.mock import Mock
from model.roles.policy_implementer import PolicyImplementer

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(PolicyImplementer, EcoRole)


@pytest.fixture
def role_before_setup():
    # Given
    model = Mock()
    role = PolicyImplementer(model)
    return role


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def role_with_env(role_before_setup):
    # Given
    env = Mock()
    role = role_before_setup
    role.env = env
    return role, env


def test_get_discount_rate_from_env(role_with_env):
    # Given
    role, env = role_with_env
    env.policy_maker.discount_rate = 0.03

    # When
    perceived = role.get_discount_rate()

    # Then
    assert perceived == 0.03


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------
