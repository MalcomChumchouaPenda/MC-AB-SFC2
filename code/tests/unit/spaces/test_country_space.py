import pytest
from dataclasses import dataclass
from unittest.mock import Mock
from mcabsfc.spaces import CountrySpace

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mcabsfc.base import EcoSpace

    # Assert
    assert issubclass(CountrySpace, EcoSpace)


def test_contains_local_markets():
    # Given
    model = Mock()
    country = CountrySpace(model)

    # Assert
    assert hasattr(country, "markets")
    assert isinstance(country.markets, dict)


@dataclass(frozen=True)
class FakeCitizenRole:
    owner: object = None
    space: object = None
    label: int = 2


@pytest.fixture
def country(monkeypatch):
    # Given a market and fake role class
    model = Mock()
    space = CountrySpace(model)
    monkeypatch.setattr("mcabsfc.spaces.CitizenRole", FakeCitizenRole)
    return space


def test_add_citizen_creates_and_registers_citizen_role(country):
    # Given
    household = Mock(id=1, roles={})

    # When
    citizen = country.add_citizen(household)

    # Then
    assert isinstance(citizen, FakeCitizenRole)
    assert citizen.owner is household
    assert citizen.space is country
    assert citizen in country.nodes
    assert citizen is household.roles["citizen"]
