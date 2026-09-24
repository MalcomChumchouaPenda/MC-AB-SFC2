from agentpy import AgentDList
from networkx import Graph
from model.base import EcoSpace, EcoRole
from model.roles.bond_buyer import BondBuyer
from model.roles.bond_issuer import BondIssuer


class BondMarket(EcoSpace):

    def setup(self):
        super().setup()
        self.issuers = AgentDList(self.model)
        self.buyers = AgentDList(self.model)

    #
    # roles
    #
    def add_issuer(self, agent):
        role = self.add_role(BondIssuer, agent, "bond_issuer")
        self.issuers.append(role)
        return role

    def add_buyer(self, agent):
        role = self.add_role(BondBuyer, agent, "bond_buyer")
        self.buyers.append(role)
        return role

    #
    # Bonds matching
    #

    def find_issuers(self):
        issuers = self.issuers
        return issuers.select(issuers.bond_number > 0)

    def find_bonds(self, issuer):
        return [
            dict(buyer=buyer, **data)
            for _, buyer, data in self.graph.edges(issuer, data=True)
        ]

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
        self.record_flow("bond_interests", issuer.id, buyer.id, interests)
        self.graph[issuer][buyer]["amount"] -= principal
