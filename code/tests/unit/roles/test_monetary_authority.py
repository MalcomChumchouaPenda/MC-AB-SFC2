import pytest
from unittest.mock import Mock
from model.roles.monetary_authority import MonetaryAuthority

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(MonetaryAuthority, EcoRole)


@pytest.fixture
def authority_before_setup():
    # Given
    model = Mock()
    authority = MonetaryAuthority(model)
    return authority


def test_expose_discount_rate_from_agent(authority_before_setup):
    # Given
    agent = Mock(discount_rate=0.02)
    authority = authority_before_setup
    authority.agent = agent

    # When
    perceived = authority.discount_rate

    # Then
    assert perceived == 0.02


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def authority_with_space(authority_before_setup):
    # Given
    space = Mock()
    authority = authority_before_setup
    authority.space = space
    return authority, space


def test_get_union_discount_rate_from_space(authority_with_space):
    # Given
    authority, space = authority_with_space
    space.union.monetary_authority.discount_rate = 0.03

    # When
    perceived = authority.get_union_discount_rate()

    # Then
    assert perceived == 0.03


def test_get_average_inflation_from_space(authority_with_space):
    # Given
    authority, space = authority_with_space
    space.average_inflation = 0.03

    # When
    perceived = authority.get_average_inflation()

    # Then
    assert perceived == 0.03


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------


def test_transfer_profits_with_space(authority_with_space):
    # Given
    authority, space = authority_with_space

    # When
    authority.transfer_profit(200)

    # Then
    space.transfer_central_bank_profits.assert_called_with(200)
