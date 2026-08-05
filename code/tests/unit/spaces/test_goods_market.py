from unittest.mock import Mock
from mcabsfc.spaces import GoodsMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mcabsfc.base import EcoSpace

    # Assert
    assert issubclass(GoodsMarket, EcoSpace)


def test_is_tradable_by_default():
    # Given
    model = Mock()
    market = GoodsMarket(model)

    # Assert
    assert market.tradable is True


def test_goods_market_can_be_non_tradable():
    # Given
    model = Mock()
    market = GoodsMarket(model, tradable=False)

    # Assert
    assert market.tradable is False

