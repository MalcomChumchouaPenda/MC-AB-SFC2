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

    def calc_gross_income(self):
        self.gross_income = (
            self.labor_income
            + self.interest_income
            + self.dividend_income
            + self.rnd_income
        )
        return self.gross_income

    def calc_disposable_income(self):
        role = self.roles["citizen"]
        tax_rate = role.get_tax_rate()
        self.disposable_income = (
            1 - tax_rate
        ) * self.gross_income + self.public_transfer
        return self.disposable_income

    def calc_expected_net_worth(self):
        return self.net_worth + self.disposable_income - self.expected_consumption

    def calc_consumption(self):
        p = self.p
        self.desired_consumption = p.cy * self.disposable_income + p.cd * self.deposits
        self.desired_trad_cons = p.cT * self.desired_consumption
        self.desired_non_trad_cons = (1 - self.p.cT) * self.desired_consumption
        return self.desired_consumption


class FirmAgent(EcoAgent):

    def setup(self):
        self.roles = {}


class BankAgent(EcoAgent):
    pass


class GovernmentAgent(EcoAgent):
    pass


class CentralBankAgent(EcoAgent):
    pass
