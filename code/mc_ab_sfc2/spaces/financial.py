from agentpy.objects import Object
from networkx import Graph
from ..base import EcoSpace
from ..roles.financial import LenderRole, BorrowerRole


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


class CreditMarket(EcoSpace):

    def add_borrower(self, firm):
        return self.add_role(BorrowerRole, firm, "borrower")

    def add_lender(self, bank):
        return self.add_role(LenderRole, bank, "lender")

    def search_lenders(self):
        return [n for n in self.nodes if isinstance(n, LenderRole)]

    def grant_loan(self, lender, borrower, amount, rate):
        borrower.loan_demand -= amount
        borrower.increase_stock("loans", amount)
        borrower.increase_stock("deposits", amount)
        lender.increase_stock("loans", amount)
        lender.increase_stock("deposits", amount)
        self.graph.add_edge(borrower, lender, amount=amount, rate=rate)


class DepositMarket(Object):

    def setup(self):
        self.deposits = Graph()

    def add_client(self, client):
        self.deposits.add_node(client, role="client")

    def add_bank(self, bank):
        self.deposits.add_node(bank, role="bank")

    def get_bank_deposits(self, bank):
        return [
            dict(client=client, **data)
            for _, client, data in self.deposits.edges(bank, data=True)
        ]

    def get_client_deposits(self, client):
        return [
            dict(bank=bank, **data)
            for _, bank, data in self.deposits.edges(client, data=True)
        ]

    def get_banks(self):
        return [
            node
            for node, data in self.deposits.nodes(data=True)
            if data and data["role"] == "bank"
        ]

    def get_defaulted_banks(self):
        return [
            node
            for node, data in self.deposits.nodes(data=True)
            if data and data["role"] == "bank" and node.defaulted
        ]

    def open_account(self, client, bank, amount=0):
        self.deposits.add_edge(client, bank, amount=amount)

    def close_account(self, client, bank):
        amount = self.deposits[client][bank]["amount"]
        bank.reserves -= amount
        client.cash += amount
        self.deposits.remove_edge(client, bank)
        return amount

    def pay_interests(self, client, bank, amount):
        deposits = self.deposits
        deposits[client][bank]["amount"] += amount
        deposits[client][bank]["interests"] = amount

    def reimburse_deposits(self, govt, client, bank):
        amount = self.deposits[client][bank]["amount"]
        govt.reserves -= amount
        client.cash += amount
        self.deposits[client][bank]["amount"] = 0

    def make_deposits(self, client, bank, amount):
        client.cash -= amount
        bank.reserves += amount
        self.deposits[client][bank]["amount"] += amount
