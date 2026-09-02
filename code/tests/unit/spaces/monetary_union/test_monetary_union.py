import pytest
from unittest.mock import Mock
from model.spaces.monetary_union import MonetaryUnion


# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from model.base import EcoSpace

    # Assert
    assert issubclass(MonetaryUnion, EcoSpace)


@pytest.fixture
def union():
    # Given
    model = Mock()
    union = MonetaryUnion(model)
    union.setup()
    return union


def test_has_union_authority_ref(union):
    # Assert
    assert union.union_authority is None


def test_has_national_authorities_list(union):
    # Assert
    assert union.national_authorities == []


def test_has_goods_market_ref(union):
    # Assert
    assert union.goods_market is None
    

def test_has_credit_market_ref(union):
    # Assert
    assert union.credit_market is None
    

def test_has_bond_market_ref(union):
    # Assert
    assert union.bond_market is None


def test_has_countries_list(union):
    # Assert
    assert union.countries == []

