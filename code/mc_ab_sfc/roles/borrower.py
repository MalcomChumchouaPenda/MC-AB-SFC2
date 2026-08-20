from ..base import EcoRole


class BorrowerRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.loan_demand = 0

    @property
    def target_leverage(self):
        agent = self.agent
        return agent.desired_loans / agent.equity

    def search_lenders(self):
        return self.space.search_lenders()

    def request_loan(self, lender):
        lender.receive_request(self)
