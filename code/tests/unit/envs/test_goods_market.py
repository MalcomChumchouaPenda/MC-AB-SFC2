import agentpy as ap
from mcabsfc.envs import GoodsMarket


def test_is_network():
    assert issubclass(GoodsMarket, ap.Network)
