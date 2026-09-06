from model.base import EcoRole


class BondBuyer(EcoRole):

    def setup(self):
        super().setup()
        self.loan_applicants = []

    #
    # Perceptions
    #
    def find_issuers(self):
        return self.space.find_issuers()

    #
    #   Actions
    #
    def buy_bonds(self, issuer, number):
        self.space.buy_bonds(self, issuer, number)
