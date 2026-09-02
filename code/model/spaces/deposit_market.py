from agentpy.objects import Object
from networkx import Graph
from model.base import EcoSpace, EcoRole


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
