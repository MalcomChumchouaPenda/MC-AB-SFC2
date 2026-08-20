from ..base import EcoRole


class BondBuyerRole(EcoRole):

    def get_bond_issuers(self):
        return self.space.get_bond_issuers()

    def buy_bonds(self, issuer, amount):
        self.space.buy_bonds(self, issuer, amount)
