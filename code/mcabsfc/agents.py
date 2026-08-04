import math
import agentpy as ap


class FirmAgent(ap.Agent):
    pass


class HouseholdAgent(ap.Agent):

    def setup(self):
        self.roles = {}
        self.labor_supply = 1.0

    def revise_reservation_wage(self):
        p = self.model.p
        role = self.roles["worker"]
        choice = self.model.nprandom.choice
        uniform = self.model.nprandom.uniform
        prob = p.upsilon_h * math.exp(-p.upsilon * role.unemployment_rate)
        if self.employed_labor == self.labor_supply:
            if choice([0, 1], p=[1 - prob, prob]):
                self.reservation_wage *= 1 + uniform(0, p.delta)
        else:
            if choice([0, 1], p=[prob, 1 - prob]):
                self.reservation_wage *= 1 - uniform(0, p.delta)

    def search_jobs(self):
        role = self.roles["worker"]
        employers = role.find_employers(self.search_size)
        accepted = [e for e in employers if e.wage >= self.reservation_wage]
        accepted.sort(key=lambda employer: employer.wage, reverse=True)
        remaining = self.labor_supply - role.labor_sold
        for employer in accepted:
            if remaining <= 0:
                break
            quantity = min(remaining, employer.demand)
            if quantity > 0:
                role.accept_job(employer, quantity)
                remaining -= quantity
