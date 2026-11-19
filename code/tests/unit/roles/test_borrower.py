import pytest
from unittest.mock import Mock
from model.roles.borrower import Borrower

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # Then
    assert issubclass(Borrower, EcoRole)


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
    return Borrower(agent, env)


def test_initializes_loan_demand(role):
    # Then
    assert role.loan_demand == 0.0


def test_initializes_defaulted(role):
    # Then
    assert role.defaulted is False


def test_exposes_net_worth_from_agent(role):
    # Given
    agent = role.agent
    agent.account = {"equities": -100}

    # When
    exposed = role.net_worth

    # Then
    assert exposed == 100


# ---------------------------------------------------
# PERCEPTIONS
# ----------------------------------------------------


@pytest.fixture
def lenders(make_dlist):
    # Given
    return make_dlist([Mock() for _ in range(5)])


def test_find_lenders_uses_env_find_method(role, env, lenders):
    # Given
    env.find_all_roles.return_value = lenders

    # When
    role.find_lenders()

    # Then
    env.find_all_roles.assert_called_with("lender")


def test_find_lenders_returns_found_roles(role, env, lenders):
    # Given
    env.find_all_roles.return_value = lenders

    # When
    result = role.find_lenders()

    # Then
    assert list(result) == list(lenders)


@pytest.fixture
def loans(make_dlist):
    # Given
    return make_dlist([Mock() for _ in range(5)])


def test_find_loans_uses_env_links(role, env, loans):
    # Given
    env.links.return_value = loans

    # When
    role.find_loans()

    # Then
    env.links.assert_called_with(role)


def test_find_loans_returns_found_links(role, env, loans):
    # Given
    env.links.return_value = loans

    # When
    result = role.find_loans()

    # Then
    assert result == loans


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


def test_repay_loans_use_env_method(role, env):
    # Given
    lender = Mock()

    # When
    role.repay_loans(lender, 100, 10)

    # Then
    env.repay_loans.assert_called_with(role, lender, 100, 10)


def test_make_defaults_use_env_method(role, env):
    # Given
    lender = Mock()

    # When
    role.make_defaults(lender, 100)

    # Then
    env.make_defaults.assert_called_with(role, lender, 100)
