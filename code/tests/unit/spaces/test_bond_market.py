from unittest.mock import Mock
from mc_ab_sfc.spaces import BondMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(BondMarket, EcoSpace)
