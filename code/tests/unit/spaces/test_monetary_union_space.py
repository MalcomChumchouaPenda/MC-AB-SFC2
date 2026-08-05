from unittest.mock import Mock
from mcabsfc.spaces import MonetaryUnionSpace

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mcabsfc.base import EcoSpace

    # Assert
    assert issubclass(MonetaryUnionSpace, EcoSpace)


def test_contains_countries():
    # Given
    model = Mock()
    union = MonetaryUnionSpace(model)

    # Assert
    assert hasattr(union, "countries")
    assert isinstance(union.countries, dict)


def test_contains_international_markets():
    # Given
    model = Mock()
    union = MonetaryUnionSpace(model)

    # Assert
    assert hasattr(union, "markets")
    assert isinstance(union.markets, dict)
