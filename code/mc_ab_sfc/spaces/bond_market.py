from ..base import EcoSpace
from ..agents import BankAgent
from ..roles import (
    BondBuyerRole,
    BondIssuerRole,
)


class BondMarket(EcoSpace):

    def add_bond_issuer(self, government):
        return self.add_role(BondIssuerRole, government, "bond_issuer")

    def add_bond_buyer(self, bank):
        return self.add_role(BondBuyerRole, bank, "bond_buyer")

    def get_bond_issuers(self):
        return [n for n in self.nodes if isinstance(n, BondIssuerRole)]

    def buy_bonds(self, buyer, issuer, amount):
        issuer.bond_supply -= amount
        issuer.increase_stock("bonds", amount)
        issuer.increase_stock("reserves", amount)
        if isinstance(buyer.agent, BankAgent):
            buyer.increase_stock("bonds", amount)
            buyer.decrease_stock("reserves", amount)
        else:
            buyer.increase_stock("bonds", amount)
            buyer.increase_stock("reserves", amount)
        self.graph.add_edge(issuer, buyer, amount=amount)

    def pay_bond_debt(self, issuer):
        graph = self.graph
        bond_rate = issuer.bond_rate
        for _, buyer in list(graph.edges(issuer)):
            principal = graph[issuer][buyer]["amount"]
            interest = bond_rate * principal
            issuer.decrease_stock("bonds", principal)
            issuer.increase_flow("bond_interest", interest)
            issuer.decrease_stock("reserves", principal + interest)
            if isinstance(buyer.agent, BankAgent):
                buyer.decrease_stock("bonds", principal)
                buyer.increase_flow("bond_interest", interest)
                buyer.increase_stock("reserves", principal + interest)
            else:
                buyer.decrease_stock("bonds", principal)
                buyer.increase_flow("bond_interest", interest)
                buyer.decrease_stock("reserves", principal + interest)
            self.graph.remove_edge(issuer, buyer)
