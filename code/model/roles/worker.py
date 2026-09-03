from model.base import EcoRole


class Worker(EcoRole):

    def setup(self):
        super().setup()
        self.labor_supply = 1.0

    #
    # perceptions method
    #
    def get_labor_sold(self):
        jobs = self.space.graph.edges(self, data=True)
        return sum(data["quantity"] for *_, data in jobs)

    def get_unemployment(self):
        return self.space.unemployment

    #
    # actions method
    #
    def find_employers(self, psi):
        employers = self.space.employers
        return employers.random(min(psi, len(employers)))

    def accept_job(self, employer, quantity):
        self.space.hire_worker(self, employer, quantity)
