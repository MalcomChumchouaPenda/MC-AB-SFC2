from ..base import EcoRole


class EquityHolderRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.equity_issuer = None
        self.share = 0.0

    @property
    def equity(self):
        return self.agent.equity

    @property
    def desired_equity(self):
        return self.agent.desired_equity

    
    def get_default_probability(self):
        return self.space.default_probability

    def get_potential_investors(self):
        return self.space.get_potential_investors(exclude=self)

    def get_bank_firm_number_ratio(self):
        country = self.space
        if len(country.firm_roles) == 0:
            return 1.0
        return len(country.bank_roles) / len(country.firm_roles)

    def get_bank_firm_equity_ratio(self):
        country = self.space
        if len(country.firm_roles) == 0:
            return 1.0
        firm_equities = sum([r.equity for r in country.firm_roles])
        bank_equities = sum([r.equity for r in country.bank_roles])
        return bank_equities / firm_equities

    def get_sector_equity_range(self, sector):
        country = self.space
        if sector == "banks":
            equities = [r.equity for r in country.bank_roles]
        else:
            firms = [r.agent for r in country.firm_roles]
            if sector == "tradable_firms":
                equities = [f.equity for f in firms if f.tradable]
            else:
                equities = [f.equity for f in firms if not f.tradable]
        if len(equities) == 0:
            return None
        return min(equities), max(equities)

    def create_firm(self, founders, tradable):
        self.space.create_firm(founders, tradable)

    def create_bank(self, founders):
        self.space.create_bank(founders)
