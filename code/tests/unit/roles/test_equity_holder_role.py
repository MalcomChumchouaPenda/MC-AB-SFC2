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



@pytest.fixture
def role():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return EquityHolderRole(agent, space)


def test_exposes_equity(role):
    # Given
    household = role.agent
    household.equity = 100

    # Assert
    assert role.equity == 100


def test_exposes_desired_equity(role):
    # Given
    household = role.agent
    household.desired_equity = 100

    # Assert
    assert role.desired_equity == 100




# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_get_default_probability(role):
    # Given
    role.space.default_probability = 0.12

    # When
    default_probability = role.get_default_probability()

    # Then
    assert default_probability == 0.12


def test_gets_potential_investors(role):
    # Given
    investors = [Mock()]
    country = role.space
    country.get_potential_investors.return_value = investors

    # When
    result = role.get_potential_investors()

    # Then
    assert result == investors



def test_gets_potential_investors_exclude_itself(role):
    # Given
    country = role.space

    # When
    role.get_potential_investors()

    # Then
    country.get_potential_investors.assert_called_with(
        exclude=role
    )

    