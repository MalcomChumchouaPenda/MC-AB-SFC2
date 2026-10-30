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

    def create_countries(self):
        for k in range(self.p.country_number):
            country = self.add_space(Country, f"country_{k}")
            country.pos = k
            country.create_markets()

    #
    # Role management
    #

    def add_central_bank(self, cb):
        self.add_role(PolicyMaker, cb)

    #
    # Cash operations
    #

    def decrease_cash(self, agent, amount):
        pos = agent.country_pos
        country = self.spaces[f"country_{pos}"]
        country.decrease_cash(agent, amount)

    def increase_cash(self, agent, amount):
        pos = agent.country_pos
        country = self.spaces[f"country_{pos}"]
        country.increase_cash(agent, amount)

    #
    # Statitics
    #

    def calc_phi_range(self):
        return self.spaces["goods_market"].calc_phi_range()

    def calc_price_range(self):
        return self.spaces["goods_market"].calc_price_range()

    def calc_sales_range(self):
        return self.spaces["goods_market"].calc_sales_range()

    #
    # Evolution
    #

    def update_state(self):
        super().update_state()
        countries = [s for k, s in self.spaces.items() if k.startswith("country")]
        gdps = [c.gdp for c in countries]
        union_gdp = sum(gdps)
        if union_gdp > 0:
            weighted_inflations = [c.gdp * c.inflation for c in countries]
            self.average_inflation = sum(weighted_inflations) / union_gdp
