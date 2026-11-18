import pytest
from unittest.mock import Mock
from model.roles.lender import Lender

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # Then
    assert issubclass(Lender, EcoRole)



@pytest.fixture
def agent():
    # Given
    return Mock()


@pytest.fixture
def env():
    # Given
    return Mock()



@pytest.fixture
def role(agent, env):
    # Given
    return Lender(agent, env)


def test_initializes_defaulted(role):
    # Then
    assert role.defaulted is False


def test_initializes_loan_applicants_list(role):
    # Then
    assert role.loan_applicants == []


# ---------------------------------------------------
#  ACTIONS
# ----------------------------------------------------


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
