from dataclasses import dataclass
import agentpy as ap


class Role(ap.AgentNode):

    def __init__(self, owner):
        super().__init__(owner.id)
        self.owner = owner

    def get_stock(self, name):
        return self.owner.stocks[name]

    def credit_stock(self, name, amount):
        if name not in self.owner.stocks:
            self.owner.stocks[name] = 0
        self.owner.stocks[name] += amount

    def debit_stock(self, name, amount):
        if name not in self.owner.stocks:
            self.owner.stocks[name] = 0
        self.owner.stocks[name] -= amount

    def get_flow(self, name):
        return self.owner.flows[name]

    def credit_flow(self, name, amount):
        if name not in self.owner.flows:
            self.owner.flows[name] = 0
        self.owner.flows[name] += amount

    def debit_flow(self, name, amount):
        if name not in self.owner.flows:
            self.owner.flows[name] = 0
        self.owner.flows[name] -= amount


class EmployerRole:
    pass


class WorkerRole(Role):

    def __init__(self, owner, market):
        super().__init__(owner)
        self.market = market

    def find_employers(self, size):
        return self.market.find_employers(size)

    def accept_job(self, employer, quantity):
        self.market.create_job(self, employer, quantity)

    @property
    def labor_sold(self):
        return self.market.labor_sold(self)

    @property
    def unemployment_rate(self):
        return self.market.unemployment_rate


class ConsumerRole(Role):

    def __init__(self, owner, market):
        super().__init__(owner)
        self.market = market
