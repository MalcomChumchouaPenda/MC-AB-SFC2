import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import CentralBankAgent

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
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


# ---------------------------------------------------
# BEHAVIORS TESTS
# ----------------------------------------------------


def test_update_discount_rate(central_bank):
    # Given
    central_role = Mock()
    central_role.get_average_inflation.return_value = 0.04
    central_bank.roles["central_bank"] = central_role
    central_bank.discount_rate = 0.03
    central_bank.p.long_run_rate = 0.02
    central_bank.p.xi = 0.5
    central_bank.p.xi_deltap = 1.5
    central_bank.p.inflation_target = 0.02

    # When
    central_bank.update_discount_rate()

    # Then
    assert central_bank.discount_rate == pytest.approx(0.04)
