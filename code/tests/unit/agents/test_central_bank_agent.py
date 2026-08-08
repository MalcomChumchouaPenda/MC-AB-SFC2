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


def test_has_default_discount_rate(central_bank):
    # Assert
    assert central_bank.discount_rate == 0


def test_has_default_stocks(central_bank):
    # Assert
    assert central_bank.reserves == 0
    assert central_bank.cash_advances == 0
