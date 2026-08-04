from dataclasses import dataclass
import agentpy as ap


@dataclass(frozen=True)
class JobOffer:
    employer: object
    wage: float
    vacancy: float


class EmployerRole:
    pass


class WorkerRole(ap.AgentNode):

    def __init__(self, owner, market):
        super().__init__(owner.id)
        self.owner = owner
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


class ConsumerRole(ap.AgentNode):

    def __init__(self, owner, market):
        super().__init__(owner.id)
        self.owner = owner
        self.market = market
