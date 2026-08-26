from ..base import EcoAgent


class CentralBankAgent(EcoAgent):

    def setup(self):
        # stocks
        self.reserves = 0
        self.cash_advances = 0

        # flows
        self.profit = 0
        self.reserve_interest = 0
        self.cash_advance_interest = 0

        # history
        self.prev_discount_rate = 0

        # decisions
        self.discount_rate = 0

        # accointances
        self.government = None

    @property
    def bonds(self):
        bond_market = self.model.bond_market
        bonds = bond_market.get_buyer_bonds(self)
        return sum([b["principal"] for b in bonds])

    @property
    def bond_interests(self):
        bond_market = self.model.bond_market
        bonds = bond_market.get_buyer_bonds(self)
        return sum([b["interests"] for b in bonds])

    def update_discount_rate(self):
        role = self.roles["central_bank"]
        role.discount_rate = self.calc_discount_rate()

    def calc_discount_rate(self):
        p = self.model.p
        role = self.roles["central_bank"]
        average_inflation = role.get_average_inflation()
        inflation_gap = average_inflation - p.inflation_target
        return (
            (1 - p.xi) * p.long_run_rate
            + p.xi * self.prev_discount_rate
            + (1 - p.xi) * p.xi_deltap * inflation_gap
        )

    def buy_remaining_bonds(self):
        govt = self.government
        bond_market = self.model.bond_market
        bond_market.buy_bonds(self, govt, govt.bond_supply)

    def pay_profit(self):
        profit = self.calc_profit()
        role = self.roles["central_bank"]
        role.transfer_profit(profit)

    def calc_profit(self):
        return self.bond_interests + self.cash_advance_interest - self.reserve_interest

    def update_history(self):
        role = self.roles["central_bank"]
        self.prev_discount_rate = role.discount_rate
