from model.base import EcoRole


class Citizen(EcoRole):

    def setup(self):
        super().setup()
        self.resid_equity = 0

    #
    # Perception methods
    #
    def get_prob_failure(self):
        return self.space.prob_failure

    def find_investors(self):
        return self.space.find_investors(initiator=self)

    def get_bank_firm_number(self):
        return self.space.calc_bank_firm_number()

    def get_bank_firm_equity(self):
        return self.space.calc_bank_firm_equity()

    def get_sector_equity_range(self, sector):
        return self.space.calc_sector_equity_range(sector)

    def get_tax_rate(self):
        return self.space.fiscal_authority.tax_rate

    #
    # Creation actions
    #
    def create_firm(self, firm, shares, tradable):
        self.space.create_firm(firm, shares, tradable)

    def create_bank(self, bank, shares):
        self.space.create_bank(bank, shares)
