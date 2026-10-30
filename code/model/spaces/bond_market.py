from model.extensions import EcoSpace
from model.roles.bond_buyer import BondBuyer
from model.roles.bond_issuer import BondIssuer


class BondMarket(EcoSpace):

    #
    # roles
    #
    def add_bank(self, bank):
        self.add_role(BondBuyer, bank)

    def add_central_bank(self, cb):
        self.add_role(BondBuyer, cb)

    def add_government(self, govt):
        self.add_role(BondIssuer, govt)

    #
    # Bonds transactions
    #

    def buy_bonds(self, buyer, issuer, number):
        amount = issuer.bond_value * number
        issuer.bond_number -= number
        env = self.env
        env.decrease_cash(buyer, amount)
        env.increase_cash(issuer, amount)
        self.transfer_stock("bonds", issuer.id, buyer.id, amount)
        self.graph.add_edge(issuer, buyer, amount=amount)

    def repay_bonds(self, buyer, issuer, principal, interests):
        repayment = principal + interests
        env = self.env
        env.increase_cash(buyer, repayment)
        env.decrease_cash(issuer, repayment)
        self.transfer_stock("bonds", buyer.id, issuer.id, principal)
        self.make_transaction("bond_interests", issuer.id, buyer.id, interests)
        self.graph[issuer][buyer]["amount"] -= principal

    #
    # Evolution
    #
    def clear_defaults(self):
        roles = self.find_all_roles("bond_buyer")
        for role in roles.select(roles.defaulted == True):
            self.remove_role(role)
