from agentpy.objects import Object
from networkx import Graph
from model.base import EcoSpace, EcoRole


class BondMarket(Object):

    def setup(self):
        self.bonds = Graph()

    def add_issuer(self, government):
        self.bonds.add_node(government, role="issuer")

    def add_buyer(self, bank):
        self.bonds.add_node(bank, role="buyer")

    def get_issuers(self):
        return [
            node
            for node, data in self.bonds.nodes(data=True)
            if data and data["role"] == "issuer"
        ]

    def get_issuer_bonds(self, issuer):
        return [
            dict(buyer=buyer, **data)
            for _, buyer, data in self.bonds.edges(issuer, data=True)
        ]

    def get_buyer_bonds(self, buyer):
        return [
            dict(issuer=issuer, **data)
            for _, issuer, data in self.bonds.edges(buyer, data=True)
        ]

    def buy_bonds(self, buyer, issuer, amount):
        issuer.bond_supply -= amount
        issuer.reserves += amount
        if buyer is issuer.central_bank:
            buyer.reserves += amount
        else:
            buyer.reserves -= amount
        self.bonds.add_edge(issuer, buyer, principal=amount)

    def repay_bonds(self, issuer, buyer, principal, interests):
        repayment = principal + interests
        issuer.reserves -= repayment
        if buyer is issuer.central_bank:
            buyer.reserves -= repayment
        else:
            buyer.reserves += repayment
        self.bonds[issuer][buyer]["principal"] -= principal
        self.bonds[issuer][buyer]["interests"] = interests
