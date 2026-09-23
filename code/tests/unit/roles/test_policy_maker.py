import pytest
from unittest.mock import Mock
from model.roles.policy_maker import PolicyMaker

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(PolicyMaker, EcoRole)


@pytest.fixture
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = PolicyMaker(agent, env)
    return role, env


def test_expose_discount_rate_from_agent(role_with_env):
    # Given
    role, _ = role_with_env
    agent = role.agent
    agent.discount_rate = 0.02

    # When
    perceived = role.discount_rate

    # Then
    assert perceived == 0.02


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------



def test_get_average_inflation_from_env(role_with_env):
    # Given
    role, env = role_with_env
    env.average_inflation = 0.03

    # When
    perceived = role.get_average_inflation()

    # Then
    assert perceived == 0.03


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------
