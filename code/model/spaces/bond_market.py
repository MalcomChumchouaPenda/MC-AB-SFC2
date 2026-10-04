from model.extensions import EcoSpace
from model.roles.bond_buyer import BondBuyer
from model.roles.bond_issuer import BondIssuer


class BondMarket(EcoSpace):

    #
    # roles
    #
    def add_bank(self, bank):
        self.add_role(BondBuyer, bank, "bond_buyer")

    def add_central_bank(self, cb):
        self.add_role(BondBuyer, cb, "bond_buyer")

    def add_government(self, govt):
        role = self.add_role(BondIssuer, govt, "bond_issuer")
        role.country_pos = govt.country_pos

    #
    # Bonds transactions
    #

    def buy_bonds(self, buyer, issuer, number):
        amount = issuer.bond_value * number
        issuer.bond_number -= number
        self.transfer_stock("bonds", issuer.id, buyer.id, amount)
        self.transfer_stock("cash", buyer.id, issuer.id, amount)
        self.graph.add_edge(issuer, buyer, amount=amount)

    def repay_bonds(self, buyer, issuer, principal, interests):
        repayment = principal + interests
        self.transfer_stock("bonds", buyer.id, issuer.id, principal)
        self.transfer_stock("cash", issuer.id, buyer.id, repayment)
        self.make_transaction("bond_interests", issuer.id, buyer.id, interests)
        self.graph[issuer][buyer]["amount"] -= principal
