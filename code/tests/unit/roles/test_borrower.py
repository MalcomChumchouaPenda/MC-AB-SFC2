import pytest
from unittest.mock import Mock
from model.roles.borrower import Borrower

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # When
    is_derived = issubclass(Borrower, EcoRole)

    # Then
    assert is_derived


def test_initializes_loan_demand():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Borrower(agent, env)

    # Then
    assert role.loan_demand == 0.0


def test_exposes_net_worth_from_env():
    # Given
    agent, env = Mock(), Mock()
    role = Borrower(agent, env)
    env.get_stock.return_value = -100

    # When
    exposed = role.net_worth

    # Then
    env.get_stock.assert_called_with("equities", agent.id)
    assert exposed == 100


# ---------------------------------------------------
# PERCEPTIONS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return Borrower(agent, env)


def test_find_lenders(role, make_dlist):
    # Given
    lender = Mock()
    env = role.env
    env.find_all_roles.return_value = make_dlist([lender])

    # When
    result = role.find_lenders()

    # Then
    env.find_all_roles.assert_called_with("lender")
    assert list(result) == [lender]


def test_find_loans(role):
    # Given
    loan = Mock()
    env = role.env
    env.links.return_value = [loan]

    # When
    result = role.find_loans()

    # Then
    env.links.assert_called_with(role, "lender")
    assert result == [loan]


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_request_loans_use_lender_method(role):
    # Given
    lender = Mock()

    # When
    role.request_loans(lender)

    # Then
    lender.receive_request.assert_called_with(role)


def test_repay_loans_use_env_method(role):
    # Given
    lender = Mock()
    env = role.env

    # When
    role.repay_loans(lender, 100, 10)

    # Then
    env.repay_loans.assert_called_with(role, lender, 100, 10)


def test_make_defaults_use_env_method(role):
    # Given
    lender = Mock()
    env = role.env

    # When
    role.make_defaults(lender, 100)

    # Then
    env.make_defaults.assert_called_with(role, lender, 100)
