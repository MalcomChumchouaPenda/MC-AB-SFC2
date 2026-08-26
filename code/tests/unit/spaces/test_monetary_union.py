import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces.monetary_union import MonetaryUnion

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(MonetaryUnion, EcoSpace)
    

@pytest.fixture
def union():
    # Given
    model = Mock()
    union = MonetaryUnion(model)
    union.setup()
    return union


def test_has_default_agent_refs(union):
    # Assert
    assert union.central_bank is None


def test_has_default_space_refs(union):
    # Assert
    assert union.goods_market is None
    assert union.credit_market is None
    assert union.bond_market is None

