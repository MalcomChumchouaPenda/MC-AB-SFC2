from model.base import EcoRole


class BondBuyer(EcoRole):

    #
    # Perceptions
    #
    def find_issuers(self):
        return self.env.find_issuers()

    #
    #   Actions
    #
    def buy_bonds(self, issuer, number):
        self.env.buy_bonds(self, issuer, number)
