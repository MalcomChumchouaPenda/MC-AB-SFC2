from model.extensions import EcoRole


class Employer(EcoRole):

    def __init__(self, agent, env, prefix=""):
        super().__init__(agent, env, prefix=prefix)
        self.wage = 0
        self.labor = 0
        self.labor_demand = 0
        self.defaulted = False

    #
    # perceptions method
    #
    def get_unemployment(self):
        return self.env.unemployment

    def get_jobs(self):
        return self.env.links(self)

    #
    # actions method
    #
    def pay_wages(self, worker, amount):
        self.env.pay_wages(self, worker, amount)
