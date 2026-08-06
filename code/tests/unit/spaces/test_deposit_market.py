
from unittest.mock import Mock
from dataclasses import dataclass
import pytest
from mc_ab_sfc.spaces import DepositMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(DepositMarket, EcoSpace)

# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------

@dataclass(frozen=True)
class FakeDepositorRole:
    owner: object = None
    space: object = None
    label: int = 2


@pytest.fixture
def market(monkeypatch):
    # Given a market and fake role class
    model = Mock()
    market = DepositMarket(model)
    monkeypatch.setattr("mc_ab_sfc.spaces.DepositorRole", FakeDepositorRole)
    return market


def test_add_depositor_creates_and_registers_depositor_role(market):
    # Given
    household = Mock(id=1, roles={})

    # When
    depositor = market.add_depositor(household)

    # Then
    assert isinstance(depositor, FakeDepositorRole)
    assert depositor.owner is household
    assert depositor.space is market
    assert depositor in market.nodes
    assert depositor is household.roles["depositor"]