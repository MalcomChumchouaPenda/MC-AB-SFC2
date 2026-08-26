import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents.central_bank import CentralBank

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from mc_ab_sfc.base import EcoAgent

    # Assert
    assert issubclass(CentralBank, EcoAgent)
