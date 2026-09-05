from model.base import EcoRole


class BondIssuer(EcoRole):

    def setup(self):
        super().setup()
        self.debt_ratio = 0
        self.bond_value = 0
        self.bond_number = 0

    #
    # Perceptions
    #
    def find_bonds(self):
        return self.space.find_bonds(self)

    #
    # Actions
    #
    def repay_bond(self, issuer, principal, interests):
        self.space.repay_bond(self, issuer, principal, interests)
