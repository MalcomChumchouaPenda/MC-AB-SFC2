import math
from functools import partial
from model.base import EcoAgent


class CentralBank(EcoAgent):

    def setup(self):
        super().setup()
        self.prev_discount_rate = 0
        self.discount_rate = 0

    #
    # Bond purchases
    #
    def buy_remaining_bonds(self):
        role = self.roles["bond_buyer"]
        for issuer in role.find_issuers():
            if issuer.country == self.country:
                role.buy_bonds(issuer, issuer.bond_number)

    #
    # Profit transfer
    #
    def transfer_profit(self):
        profit = self.calc_profit()
        role = self.roles["monetary_authority"]
        role.transfer_profit(profit)

    def calc_profit(self):
        flows = self.account.flows
        return (
            flows["bond_interests"] + flows["adv_interests"] - flows["cash_interests"]
        )

    #
    # Monetary policy
    #
    def calc_discount_rate(self):
        p = self.model.p
        average_inflation = self.average_inflation
        inflation_gap = average_inflation - p.inflation_target
        return (
            (1 - p.xi) * p.long_run_rate
            + p.xi * self.prev_discount_rate
            + (1 - p.xi) * p.xi_deltap * inflation_gap
        )

    def determine_discount_rate(self):
        role = self.roles["monetary_authority"]
        old_discount_rate = self.discount_rate
        self.average_inflation = role.get_average_inflation()
        self.discount_rate = self.calc_discount_rate()
        self.prev_discount_rate = old_discount_rate

    def implement_discount_rate(self):
        role = self.roles["monetary_authority"]
        old_discount_rate = self.discount_rate
        self.discount_rate = role.get_union_discount_rate()
        self.prev_discount_rate = old_discount_rate
