from model.base import EcoRole


class Worker(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.labor_supply = 1.0

    #
    # perceptions method
    #

    @property
    def labor_sold(self):
        return 1.0 - self.labor_supply

    def get_unemployment(self):
        return self.env.unemployment

    #
    # actions method
    #

    def find_employers(self, psi):
        return self.env.find_employers(psi)

    def accept_job(self, employer, quantity):
        self.env.hire_worker(self, employer, quantity)
