import pytest
from unittest.mock import Mock
from model.agents.central_bank import CentralBank

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from model.base import EcoAgent

    # Assert
    assert issubclass(CentralBank, EcoAgent)


@pytest.fixture
def cb_before_setup():
    # Given
    model = Mock()
    cb = CentralBank(model)
    return cb


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def cb_as_bond_buyer(cb_before_setup):
    # Given
    role = Mock()
    cb = cb_before_setup
    cb.roles = {"bond_buyer": role}
    cb.country = 1
    return cb, role


def test_buy_all_domestic_remaining_bonds(cb_as_bond_buyer):
    # Given
    issuer = Mock(country=1, bond_number=5)
    cb, role = cb_as_bond_buyer
    role.find_issuers.return_value = [issuer]

    # When
    cb.buy_remaining_bonds()

    # Then
    role.buy_bonds.assert_called_with(issuer, 5)


def test_dont_buy_foreign_bonds(cb_as_bond_buyer):
    # Given
    issuer = Mock(country=2, bond_number=5)
    cb, role = cb_as_bond_buyer
    role.find_issuers.return_value = [issuer]

    # When
    cb.buy_remaining_bonds()

    # Then
    role.buy_bonds.assert_not_called()
