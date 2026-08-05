from unittest.mock import Mock
from mcabsfc.spaces import EquityMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mcabsfc.base import EcoSpace

    # Assert
    assert issubclass(EquityMarket, EcoSpace)
