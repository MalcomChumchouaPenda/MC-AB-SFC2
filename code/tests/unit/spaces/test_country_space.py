import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import CountrySpace

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(CountrySpace, EcoSpace)


def test_contains_local_markets():
    # Given
    model = Mock()
    country = CountrySpace(model)

    # Assert
    assert hasattr(country, "markets")
    assert isinstance(country.markets, dict)


class FakeRole:
    pass


@pytest.fixture
def country():
    # Given
    model = Mock()
    space = CountrySpace(model)
    return space


def test_add_citizen_creates_citizen_role(country, monkeypatch):
    # Given
    household = Mock()
    country.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.CitizenRole", FakeRole)

    # When
    citizen = country.add_citizen(household)

    # Then
    action = country.add_role
    action.assert_called_with(FakeRole, household, "citizen")
    assert citizen is action.return_value
