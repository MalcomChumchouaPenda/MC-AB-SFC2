import pytest
from unittest.mock import Mock
from model.roles.deposit_guarantee import DepositGuarantee

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.base import EcoRole

    # When
    is_derived = issubclass(DepositGuarantee, EcoRole)

    # Then
    assert is_derived


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return DepositGuarantee(agent, env)


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_find_defaults_from_env(role, make_dlist):
    # Given
    bad = Mock(defaulted=True, id=1)
    good = Mock(defaulted=False, id=2)
    env = role.env
    env.find_all_roles.return_value = make_dlist([bad, good])
    env.get_stock = lambda x, y: -100 * y if x == "deposits" else 0

    # When
    found = role.find_defaults()

    # Then
    env.find_all_roles.assert_called_with("deposit_bank")
    assert found == [{"bank": bad, "amount": -100}]


def test_find_deposits_from_env(role):
    # Given
    bank = Mock()
    env = role.env

    # When
    found = role.find_deposits(bank)

    # Then
    env.find_links.assert_called_with(bank, "depositor")
    assert found == env.find_links.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_reimburse_deposits_into_env(role):
    # Given
    env = role.env
    depositor = Mock()

    # When
    role.reimburse_deposits(depositor, 200)

    # Then
    env.reimburse_deposits.assert_called_with(role, depositor, 200)
