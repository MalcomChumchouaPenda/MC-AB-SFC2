from model.extensions import EcoRole


class Borrower(EcoRole):

    def __init__(self, agent_id, env):
        super().__init__(agent_id, env)
        self.loan_demand = 0
        self.net_worth = 0

    #
    # Perceptions
    #
    def find_lenders(self):
        return self.env.find_all_roles("lender")

    def find_loans(self):
        return self.env.find_links(self, "lender")

    #
    # Actions
    #
    def request_loans(self, lender):
        lender.receive_request(self)

    def repay_loans(self, lender, principal, interests):
        self.env.repay_loans(self, lender, principal, interests)

    def make_defaults(self, lender, amount):
        self.env.make_defaults(self, lender, amount)
