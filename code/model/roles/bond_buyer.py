from model.base import EcoRole


class BondBuyer(EcoRole):

    #
    # Perceptions
    #
    def find_issuers(self):
        issuers = self.env.find_all_roles("bond_issuer")
        return issuers.select(issuers.bond_number > 0)

    #
    #   Actions
    #
    def buy_bonds(self, issuer, number):
        self.env.buy_bonds(self, issuer, number)
