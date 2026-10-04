from model.extensions import EcoRole


class Employer(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.wage = 0
        self.labor_demand = 0

    #
    # perceptions method
    #
    def get_unemployment(self):
        return self.env.unemployment

    def get_jobs(self):
        return self.env.links(self, "worker")

    #
    # actions method
    #
    def pay_wages(self, worker, amount):
        self.env.pay_wages(self, worker, amount)

