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


def test_expose_discount_rate_from_space(authority_with_space):
    # Given
    authority, space = authority_with_space
    space.discount_rate = 0.02

    # When
    perceived = authority.discount_rate

    # Then
    assert perceived == 0.02


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_change_discount_rate_into_space(authority_with_space):
    # Given
    authority, space = authority_with_space

    # When
    authority.discount_rate = 0.05

    # Then
    assert space.discount_rate == 0.05
