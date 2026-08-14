import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import DepositGuaranteeRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(DepositGuaranteeRole, EcoRole)


@pytest.fixture
def role():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return DepositGuaranteeRole(agent, space)


def test_get_defaulted_banks(role):
    # Given
    banks = [Mock()]
    market = role.space
    market.get_defaulted_banks.return_value = banks

    # When
    result = role.get_defaulted_banks()

    # Then
    assert result == banks


def test_reimburse_deposits(role):
    # Given
    bank = Mock()
    market = role.space

    # When
    role.reimburse_deposits(bank)

    # Then
    market.reimburse_deposits.assert_called_with(role, bank)

