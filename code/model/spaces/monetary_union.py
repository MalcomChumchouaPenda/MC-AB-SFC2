from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.policy_maker import PolicyMaker
from model.roles.policy_implementer import PolicyImplementer
from model.spaces.country import Country
from model.spaces.good_market import GoodsMarket
from model.spaces.credit_market import CreditMarket
from model.spaces.bond_market import BondMarket


class MonetaryUnion(EcoSpace):

    def setup(self):
        super().setup()
        self.gdp = 0
        self.average_inflation = 0
        self.policy_maker = None
        self.policy_implementers = AgentDList(self.model)
        self.add_space(GoodsMarket, "good_market", tradable=True)
        self.add_space(CreditMarket, "credit_market")
        self.add_space(BondMarket, "bond_market")
        for k in range(self.model.p.K):
            self.add_space(Country, f"country_{k}")

    #
    # Role management
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
        self.spaces["credit_market"].add_borrower(firm)
        if tradable:
            self.spaces["good_market"].add_producer(firm)

    #
    # Bank creation
    #
    def place_bank(self, bank):
        self.spaces["credit_market"].add_lender(bank)
        self.spaces["bond_market"].add_buyer(bank)

    #
    # Evolution
    #
    def update_average_inflation(self):
        countries = [s for k, s in self.spaces.items() if k.startswith("country")]
        gdps = [c.gdp for c in countries]
        weighted_inflations = [c.gdp * c.inflation for c in countries]
        self.average_inflation = sum(weighted_inflations) / sum(gdps)
