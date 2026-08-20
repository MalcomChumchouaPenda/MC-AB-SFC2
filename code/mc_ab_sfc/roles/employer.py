from ..base import EcoRole


class EmployerRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.labor_demand = 0

    @property
    def wage_offer(self):
        return self.agent.wage_offer
