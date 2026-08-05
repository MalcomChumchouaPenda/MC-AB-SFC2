import math
import agentpy as ap
from .base import EcoAgent


class HouseholdAgent(EcoAgent):

    def setup(self):
        self.roles = {}
        self.labor_supply = 1.0

    def calc_revision_probability(self):
        p = self.p
        role = self.roles["worker"]
        unemployment = role.get_unemployment_rate()
        return p.upsilon_h * math.exp(-p.upsilon * unemployment)

    def revise_reservation_wage(self):
        p = self.p
        random = self.model.nprandom
        prob = self.calc_revision_probability()
        if self.employed_labor == self.labor_supply:
            if random.choice([0, 1], p=[1 - prob, prob]):
                self.reservation_wage *= 1 + random.uniform(0, p.delta)
        else:
            if random.choice([0, 1], p=[prob, 1 - prob]):
                self.reservation_wage *= 1 - random.uniform(0, p.delta)

    def search_jobs(self):
        p = self.p
        role = self.roles["worker"]
        employers = role.search_employers(p.psi)
        accepted = [e for e in employers if e.wage >= self.reservation_wage]
        accepted.sort(key=lambda employer: employer.wage, reverse=True)
        remaining = self.labor_supply - role.get_labor_sold()
        for employer in accepted:
            if remaining <= 0:
                break
            quantity = min(remaining, employer.demand)
            if quantity > 0:
                role.create_job(employer, quantity)
                remaining -= quantity


class FirmAgent(EcoAgent):

    def setup(self):
        self.roles = {}


class BankAgent(EcoAgent):
    pass


class GovernmentAgent(EcoAgent):
    pass


class CentralBankAgent(EcoAgent):
    pass
