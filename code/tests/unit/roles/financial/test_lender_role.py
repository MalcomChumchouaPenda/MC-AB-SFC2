import pytest
from unittest.mock import Mock
from model.roles.financial import LenderRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(LenderRole, EcoRole)


@pytest.fixture
def lender():
    # Given
    market = Mock()
    agent = Mock(id=1)
    return LenderRole(agent, market)


def test_has_loan_applicants_list(lender):
    # Assert
    assert lender.loan_applicants == []


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_receive_request(lender):
    # Given
    borrower = Mock()

    # When
    lender.receive_request(borrower)

    # Then
    assert lender.loan_applicants == [borrower]


def test_grant_loan(lender):
    # Given
    borrower = Mock()
    market = lender.space

    # When
    lender.grant_loan(borrower, 100, 0.04)

    # Then
    action = market.grant_loan
    action.assert_called_once_with(lender, borrower, 100, 0.04)
