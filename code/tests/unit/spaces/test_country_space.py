import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import CountrySpace

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(CountrySpace, EcoSpace)


@pytest.fixture
def country():
    # Given
    model = Mock()
    space = CountrySpace(model)
    return space


def test_contains_local_markets(country):
    # Assert
    assert hasattr(country, "markets")
    assert isinstance(country.markets, dict)


def test_has_default_tax_rate(country):
    # Assert
    assert country.tax_rate == 0


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


class FakeRole:
    pass


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


def test_add_tax_payer_creates_tax_payer_role(country, monkeypatch):
    # Given
    agent = Mock()
    country.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.TaxPayerRole", FakeRole)

    # When
    tax_payer = country.add_tax_payer(agent)

    # Then
    action = country.add_role
    action.assert_called_with(FakeRole, agent, "tax_payer")
    assert tax_payer is action.return_value
