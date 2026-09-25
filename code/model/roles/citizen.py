from model.base import EcoRole


class Citizen(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.resid_equity = 0

    #
    # Perception methods
    #
    def get_prob_failure(self):
        return self.env.prob_failure

    def find_investors(self):
        citizens = self.env.find_all_roles("citizens")
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
        return self.env.fiscal_authority.tax_rate

    #
    # Creation actions
    #
    def create_firm(self, firm, shares, tradable):
        self.env.create_firm(firm, shares, tradable)

    def create_bank(self, bank, shares):
        self.env.create_bank(bank, shares)

    def pay_taxes(self, amount):
        self.env.pay_taxes(self, amount)
