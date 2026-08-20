
from ..base import EcoAgent


class CentralBankAgent(EcoAgent):

    def setup(self):
        # stocks
        self.bonds = 0
        self.reserves = 0
        self.cash_advances = 0

        # flows
        self.profit = 0
        self.bond_interest = 0
        self.reserve_interest = 0
        self.cash_advance_interest = 0

        # history
        self.prev_discount_rate = 0

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
        role = self.roles["bond_buyer"]
        bond_issuers = role.get_bond_issuers()
        for issuer in bond_issuers:
            purchase = issuer.bond_supply
            role.buy_bonds(issuer, purchase)

    def pay_profit(self):
        profit = self.calc_profit()
        role = self.roles["central_bank"]
        role.transfer_profit(profit)

    def calc_profit(self):
        return self.bond_interest + self.cash_advance_interest - self.reserve_interest

    def update_history(self):
        role = self.roles["central_bank"]
        self.prev_discount_rate = role.discount_rate
