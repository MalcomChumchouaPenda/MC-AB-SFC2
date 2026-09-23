from agentpy import AgentDList
from model.base import EcoEnv
from model.roles.policy_maker import PolicyMaker
from model.roles.policy_implementer import PolicyImplementer
from model.spaces.country import Country
from model.spaces.good_market import GoodsMarket
from model.spaces.credit_market import CreditMarket
from model.spaces.bond_market import BondMarket


class MonetaryUnion(EcoEnv):

    def setup(self):
        super().setup()
        self.gdp = 0
        self.average_inflation = 0
        self.policy_maker = None
        self.policy_implementers = AgentDList(self.model)
        self._setup_countries(self.model)
        self._setup_markets(self.model)

    def _setup_countries(self, model):
        countries = []
        for _ in range(model.p.K):
            country = Country(model)
            country.setup()
            country.union = self
            countries.append(country)
        self.countries = countries

    def _setup_markets(self, model):
        self.good_market = GoodsMarket(model)
        self.good_market.setup()
        self.good_market.tradable = True
        self.credit_market = CreditMarket(model)
        self.credit_market.setup()
        self.bond_market = BondMarket(model)
        self.bond_market.setup()

    #
    # Role / Account management
    #
    def add_policy_maker(self, agent):
        role = self.add_role(PolicyMaker, agent, "policy_maker")
        self.policy_maker = role
        return role

    def add_policy_implementer(self, agent):
        role = self.add_role(PolicyImplementer, agent, "policy_implementer")
        self.policy_implementers.append(role)
        return role

    #
    # Firm creation
    #
    def place_firm(self, firm, tradable):
        self.credit_market.add_borrower(firm)
        if tradable:
            self.good_market.add_producer(firm)

    #
    # Bank creation
    #
    def place_bank(self, bank):
        self.credit_market.add_lender(bank)
        self.bond_market.add_buyer(bank)

    #
    # Cash transactions
    #
    def transfer_cash(self, source, target, amount):
        source.account.debit_stock("cash", amount)
        target.account.credit_stock("cash", amount)

    #
    # Evolution
    #
    def update_average_inflation(self):
        countries = self.countries
        gdps = [c.gdp for c in countries.values()]
        weighted_inflations = [c.gdp * c.inflation for c in countries.values()]
        self.average_inflation = sum(weighted_inflations) / sum(gdps)
