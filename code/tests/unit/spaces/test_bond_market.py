from unittest.mock import Mock
from mcabsfc.spaces import BondMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mcabsfc.base import EcoSpace

    # Assert
    assert issubclass(BondMarket, EcoSpace)
