from model.base import EcoRole


class BondIssuer(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.debt_ratio = 0
        self.bond_value = 0
        self.bond_number = 0

    #
    # Perceptions
    #
    def find_bonds(self):
        return self.env.find_links(self, "buyer")

    def get_discount_rate(self):
        return self.env.discount_rate

    #
    # Actions
    #
    def repay_bonds(self, buyer, principal, interests):
        self.env.repay_bonds(buyer, self, principal, interests)
