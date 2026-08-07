import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import EquitySpace

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(EquitySpace, EcoSpace)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


class FakeRole:
    pass


@pytest.fixture
def space():
    # Given
    model = Mock()
    space = EquitySpace(model)
    return space


def test_add_equity_holder_creates_appropriate_role(space, monkeypatch):
    # Given
    household = Mock()
    space.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityHolderRole", FakeRole)

    # When
    equity_holder = space.add_equity_holder(household)

    # Then
    space.add_role.assert_called_with(FakeRole, household, "equity_holder")
    assert equity_holder is space.add_role.return_value


def test_add_equity_issuer_creates_appropriate_role(space, monkeypatch):
    # Given
    agent = Mock()
    space.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityIssuerRole", FakeRole)

    # When
    equity_issuer = space.add_equity_issuer(agent)

    # Then
    space.add_role.assert_called_with(FakeRole, agent, "equity_issuer")
    assert equity_issuer is space.add_role.return_value
