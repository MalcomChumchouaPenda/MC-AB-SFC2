import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import EquityHolderRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(EquityHolderRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return EquityHolderRole(agent, space)


def test_get_default_probability(role):
    # Given
    role.space.default_probability = 0.12

    # When
    default_probability = role.get_default_probability()

    # Then
    assert default_probability == 0.12
