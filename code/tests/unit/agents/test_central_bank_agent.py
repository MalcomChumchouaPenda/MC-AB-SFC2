import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import CentralBankAgent

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecoagent():
    # Given
    from mc_ab_sfc.base import EcoAgent

    # Assert
    assert issubclass(CentralBankAgent, EcoAgent)


@pytest.fixture
def central_bank():
    # Given
    model = Mock()
    return CentralBankAgent(model)
