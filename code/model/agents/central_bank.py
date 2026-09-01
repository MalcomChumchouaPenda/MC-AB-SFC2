import math
from functools import partial
from model.base import EcoAgent



class CentralBank(EcoAgent):

    def setup(self):

        # flows

        # accointances
        self.government = None

    @property
    def bonds(self):
        bond_market = self.country.union.bond_market
        bonds = bond_market.get_buyer_bonds(self)
        return sum([b["principal"] for b in bonds])

    @property
    def bond_interests(self):
        bond_market = self.country.union.bond_market
        bonds = bond_market.get_buyer_bonds(self)
        return sum([b["interests"] for b in bonds])

    def buy_remaining_bonds(self):
        govt = self.government
        bond_market = self.country.union.bond_market
        bond_market.buy_bonds(self, govt, govt.bond_supply)

    def pay_profit(self):
        profit = self.calc_profit()
        role = self.roles["central_bank"]
        role.transfer_profit(profit)

    def calc_profit(self):
        return self.bond_interests + self.cash_advance_interest - self.reserve_interest


class NationalCentralBank(CentralBank):

    def setup(self):
        # stocks
        self.reserves = 0
        self.cash_advances = 0

        # flows
        self.profits = 0
        self.reserve_interest = 0
        self.cash_advance_interest = 0

        # indicators
        self.country = None

        # accointances
        self.union_bank = None
        self.government = None

    @property
    def discount_rate(self):
        union_cb = self.union_bank
        if union_cb is None:
            return 0.0
        return union_cb.discount_rate

    def transfer_profit(self):
        amount = self.calc_profit()
        govt = self.government
        govt.profits += amount
        govt.reserves += amount
        self.profits += amount
        self.reserves += amount


class UnionCentralBank(CentralBank):

    def setup(self):
        # history
        self.prev_discount_rate = 0
        self.average_inflation = 0

        # decisions
        self.discount_rate = 0

    def calc_average_inflation(self):
        markets = self.model.national_goods_markets
        gdps = [m.gdp for m in markets.values()]
        weighted_inflations = [m.gdp * m.inflation for m in markets.values()]
        return sum(weighted_inflations) / sum(gdps)

    def calc_discount_rate(self):
        p = self.model.p
        average_inflation = self.average_inflation
        inflation_gap = average_inflation - p.inflation_target
        return (
            (1 - p.xi) * p.long_run_rate
            + p.xi * self.prev_discount_rate
            + (1 - p.xi) * p.xi_deltap * inflation_gap
        )

    def update_discount_rate(self):
        old_discount_rate = self.discount_rate
        self.average_inflation = self.calc_average_inflation()
        self.discount_rate = self.calc_discount_rate()
        self.prev_discount_rate = old_discount_rate
