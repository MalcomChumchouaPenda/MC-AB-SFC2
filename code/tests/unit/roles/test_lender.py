import pytest
from unittest.mock import Mock
from model.roles.lender import Lender

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # When
    is_derived = issubclass(Lender, EcoRole)

    # Then
    assert is_derived


def test_initializes_loan_applicants_list():
    # Given
    env = Mock()
    agent_id = 1

    # When
    role = Lender(agent_id, env)

    # Then
    assert role.loan_applicants == []


# ---------------------------------------------------
#  ACTIONS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    env = Mock()
    agent_id = 1
    return Lender(agent_id, env)


def test_receive_request(role):
    # Given
    borrower = Mock()
    role.loan_applicants = []

    # When
    role.receive_request(borrower)

    # Then
    assert role.loan_applicants == [borrower]


def test_grant_loan(role):
    # Given
    borrower = Mock()
    env = role.env

    # When
    role.grant_loan(borrower, 100, 0.04)

    # Then
    env.grant_loan.assert_called_with(role, borrower, 100, 0.04)
