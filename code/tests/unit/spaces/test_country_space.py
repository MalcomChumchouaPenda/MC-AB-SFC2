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
