import math
from functools import partial
from model.base import EcoAgent


class CentralBank(EcoAgent):

    def setup(self):
        super().setup()
        self.prev_discount_rate = 0

    #
    # Bond purchases
    #
    def buy_remaining_bonds(self):
        role = self.roles["bond_buyer"]
        for issuer in role.find_issuers():
            if issuer.country_id == self.country_id:
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
        role = self.roles["policy_maker"]
        average_inflation = role.get_average_inflation()
        inflation_gap = average_inflation - p.inflation_target
        return (
            (1 - p.xi) * p.long_run_rate
            + p.xi * self.prev_discount_rate
            + (1 - p.xi) * p.xi_deltap * inflation_gap
        )

    def determine_discount_rate(self):
        role = self.roles["policy_maker"]
        old_discount_rate = role.get_discount_rate()
        new_discount_rate = self.calc_discount_rate()
        role.set_discount_rate(new_discount_rate)
        self.prev_discount_rate = old_discount_rate

    def implement_discount_rate(self):
        maker_role = self.roles["policy_maker"]
        discount_rate = maker_role.get_discount_rate()
        auth_role = self.roles["monetary_authority"]
        auth_role.discount_rate = discount_rate
        self.prev_discount_rate = discount_rate
