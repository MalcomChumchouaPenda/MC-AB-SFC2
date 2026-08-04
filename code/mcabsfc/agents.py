import agentpy as ap


class FirmAgent(ap.Agent):
    pass


class HouseholdAgent(ap.Agent):

    def setup(self):
        self.roles = {}
        self.labor_supply = 1.0

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
