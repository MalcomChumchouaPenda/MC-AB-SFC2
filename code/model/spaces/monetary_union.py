from ..base import EcoSpace
from ..agents.firm import Firm
from ..agents.bank import Bank
from ..roles.institutionnal import EquityHolderRole, EquityIssuerRole


class MonetaryUnion(EcoSpace):

    def setup(self):
        # agent refs
        self.central_bank = None

        # space refs
        self.goods_market = None
        self.credit_market = None
        self.bond_market = None

