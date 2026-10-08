from model.extensions import EcoRole


class Citizen(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.resid_equity = 0
        self.company_number = 0

    #
    # Perception methods
    #
    def get_prob_failure(self):
        return self.env.prob_failure

    def find_investors(self):
        citizens = self.env.find_all_roles("citizen")
        investors = citizens.select(citizens.resid_equity > 0)
        if self in investors:
            investors.remove(self)
        return investors

    def get_bank_number_ratio(self):
        return self.env.calc_bank_number_ratio()

    def get_bank_equity_ratio(self):
        return self.env.calc_bank_equity_ratio()

    def get_sector_equity_range(self, sector):
        return self.env.calc_sector_equity_range(sector)

    def get_tax_rate(self):
        return self.env.tax_rate

    def get_average_wage(self):
        return self.env.average_wage

    #
    # Creation actions
    #
    def fund_company(self, agent_id, amount):
        company = self.env.roles[agent_id]
        self.env.fund_company(company, self, amount)

    def pay_taxes(self, amount):
        self.env.pay_taxes(self, amount)
