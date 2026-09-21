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
def role_before_setup():
    # Given
    model = Mock()
    role = PolicyMaker(model)
    return role


def test_expose_discount_rate_from_agent(role_before_setup):
    # Given
    agent = Mock(discount_rate=0.02)
    role = role_before_setup
    role.agent = agent

    # When
    perceived = role.discount_rate

    # Then
    assert perceived == 0.02


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


def test_get_average_inflation_from_space(role_with_space):
    # Given
    role, space = role_with_space
    space.average_inflation = 0.03

    # When
    perceived = role.get_average_inflation()

    # Then
    assert perceived == 0.03



# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------