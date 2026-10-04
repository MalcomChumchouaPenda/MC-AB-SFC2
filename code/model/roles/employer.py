from model.extensions import EcoRole


class Employer(EcoRole):

    def __init__(self, agent_id, env):
        super().__init__(agent_id, env)
        self.wage = 0
        self.labor_demand = 0

    #
    # perceptions method
    #
    def get_unemployment(self):
        return self.env.unemployment

    def get_jobs(self):
        return self.env.find_links(self, "worker")
