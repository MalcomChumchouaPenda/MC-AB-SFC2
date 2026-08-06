from unittest.mock import Mock
from dataclasses import dataclass
import pytest
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


@dataclass(frozen=True)
class FakeHolderRole:
    owner: object = None
    space: object = None
    label: int = 1


@dataclass(frozen=True)
class FakeEntityRole:
    owner: object = None
    space: object = None
    label: int = 2


@pytest.fixture
def space(monkeypatch):
    # Given a space and fake role class
    model = Mock()
    space = EquitySpace(model)
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityHolderRole", FakeHolderRole)
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityEntityRole", FakeEntityRole)
    return space


def test_add_equity_holder_creates_and_registers_appropriate_role(space):
    # Given
    household = Mock(id=1, roles={})
    space.tradable = False

    # When
    equity_holder = space.add_equity_holder(household)

    # Then
    assert isinstance(equity_holder, FakeHolderRole)
    assert equity_holder.owner is household
    assert equity_holder.space is space
    assert equity_holder in space.nodes
    assert equity_holder is household.roles["equity_holder"]


def test_add_equity_entity_creates_and_registers_appropriate_role(space):
    # Given
    agent = Mock(id=1, roles={})

    # When
    equity_entity = space.add_equity_entity(agent)

    # Then
    assert isinstance(equity_entity, FakeEntityRole)
    assert equity_entity.owner is agent
    assert equity_entity.space is space
    assert equity_entity in space.nodes
    assert equity_entity is agent.roles["equity_entity"]
