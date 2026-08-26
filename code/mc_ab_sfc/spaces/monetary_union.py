from ..base import EcoSpace


class MonetaryUnion(EcoSpace):

    def setup(self):
        # agent refs
        self.central_bank = None

        # space refs
        self.goods_market = None
        self.credit_market = None
        self.bond_market = None
