
from model.base import EcoSpace


class MonetaryUnion(EcoSpace):

    def setup(self):
        self.union_authority = None
        self.national_authorities = []
        self.goods_market = None
        self.credit_market = None
        self.bond_market = None
        self.countries = []

