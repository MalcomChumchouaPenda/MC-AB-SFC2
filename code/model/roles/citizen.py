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
        citizens = self.space.citizens
        investors = citizens.select(citizens.resid_equity > 0)
        if self in investors:
            investors.remove(self)
        return investors

    def get_bank_firm_ratios(self):
        companies = self.space.companies
        print(companies)
        firm_sector = companies.select([c.sector[0] == "F" for c in companies])
        bank_sector = companies.select(companies.sector == "B")
        if len(firm_sector) == 0:
            return 1.0, 1.0
        ratio1 = len(bank_sector) / len(firm_sector)
        ratio2 = sum(bank_sector.equity) / sum(firm_sector.equity)
        return ratio1, ratio2

    def get_sector_equity_range(self, sector):
        economy = self.space
        equities = [c.equity for c in economy.companies if c.sector == sector]
        if len(equities) == 0:
            return None
        return min(equities), max(equities)

    #
    # Creation actions
    #
    def create_firm(self, firm, shares, tradable):
        self.space.create_firm(firm, shares, tradable)

    def create_bank(self, bank, shares):
        self.space.create_bank(bank, shares)
