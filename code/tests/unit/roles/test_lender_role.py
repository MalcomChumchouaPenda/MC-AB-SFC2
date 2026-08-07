import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import LenderRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(LenderRole, EcoRole)


@pytest.fixture
def lender():
    # Given
    market = Mock()
    owner = Mock(id=1)
    return LenderRole(owner, market)


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
