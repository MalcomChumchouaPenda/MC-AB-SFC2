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
        return self.env.find_bonds(self)

    def get_discount_rate(self):
        return self.env.discount_rate

    #
    # Actions
    #
    def repay_bonds(self, buyer, principal, interests):
        self.env.repay_bonds(buyer, self, principal, interests)
