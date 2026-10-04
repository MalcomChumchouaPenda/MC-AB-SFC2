from model.extensions import EcoSpace
from model.roles.policy_maker import PolicyMaker
from model.spaces.country import Country
from model.spaces.goods_market import GoodsMarket
from model.spaces.credit_market import CreditMarket
from model.spaces.bond_market import BondMarket


class MonetaryUnion(EcoSpace):

    def setup(self):
        super().setup()
        self.gdp = 0
        self.average_inflation = 0
        self.discount_rate = 0.0

    def create_markets(self):
        self.add_space(GoodsMarket, "goods_market", tradable=True)
        self.add_space(CreditMarket, "credit_market")
        self.add_space(BondMarket, "bond_market")

    def create_countries(self, number):
        for k in range(number):
            country = self.add_space(Country, f"country_{k}")
            country.create_markets()

    #
    # Role management
    #
    def add_household(self, household):
        c = household.country_pos
        self.spaces[f"country_{c}"].add_household(household)
        self.spaces["goods_market"].add_household(household)

    def add_firm(self, firm):
        for name, space in self.spaces.items():
            if name.startswith("country_"):
                space.add_firm(firm)
            elif name == "credit_market":
                space.add_firm(firm)
            elif name == "goods_market" and firm.tradable:
                space.add_firm(firm)

    def add_bank(self, bank):
        c = bank.country_pos
        self.spaces[f"country_{c}"].add_bank(bank)
        self.spaces["credit_market"].add_bank(bank)
        self.spaces["bond_market"].add_bank(bank)

    def add_government(self, govt):
        c = govt.country_pos
        self.spaces[f"country_{c}"].add_government(govt)
        self.spaces["bond_market"].add_government(govt)

    def add_central_bank(self, cb):
        self.add_role(PolicyMaker, cb, "policy_maker")
        self.spaces["bond_market"].add_central_bank(cb)
        if cb.national:
            c = cb.country_pos
            self.spaces[f"country_{c}"].add_central_bank(cb)

    #
    # Evolution
    #
    def update_average_inflation(self):
        countries = [s for k, s in self.spaces.items() if k.startswith("country")]
        gdps = [c.gdp for c in countries]
        weighted_inflations = [c.gdp * c.inflation for c in countries]
        self.average_inflation = sum(weighted_inflations) / sum(gdps)
