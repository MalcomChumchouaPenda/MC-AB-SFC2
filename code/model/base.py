from agentpy import Agent, Network, AgentDList
from agentpy.objects import Object


class EcoAgent(Agent):
    """
    Classe de base des agents économiques.

    Un agent possède un ensemble de rôles.
    """

    def setup(self):
        self.roles = {}
        self.country = 0
        self.account = None
        self.cb_account = None
        self.bank_account = None


class EcoRole(Object):
    """
    Classe de base des rôles économiques.

    Un rôle est un proxy de l'agent propriétaire
    et un adaptateur vers un espace d'interaction.
    """

    def setup(self):
        super().setup()
        self.agent = None
        self.space = None
        self.name = ""

    @property
    def country(self):
        return self.agent.country

    @property
    def account(self):
        return self.agent.account
    
    @property
    def cb_account(self):
        return self.agent.cb_account

    @property
    def bank_account(self):
        return self.agent.bank_account

    @bank_account.setter
    def bank_account(self, account):
        self.agent.bank_account = account

    def debit_stock(self, name, amount):
        self.agent.account.debit_stock(name, amount)

    def credit_stock(self, name, amount):
        self.agent.account.credit_stock(name, amount)

    def debit_flow(self, name, amount):
        self.agent.account.debit_flow(name, amount)

    def credit_flow(self, name, amount):
        self.agent.account.credit_flow(name, amount)

    def clear_flows(self):
        self.agent.account.clear_flows()


class EcoSpace(Network):
    """
    Classe de base des espaces d'interaction.

    Un espace contient des rôles qui correspondent
    à ses noeuds.
    """

    def setup(self):
        self.roles = {}
        self.root_space = None
        self.sub_spaces = {}

    def add_space(self, sub_space, name):
        sub_space.root_space = self
        self.sub_spaces[name] = sub_space

    def evolve(self):
        for sub_space in self.sub_spaces.values():
            sub_space.update_state()
            sub_space.clear_defaults()
        self.update_state()
        self.clear_defaults()

    def update_state(self):
        raise NotImplementedError

    def clear_defaults(self):
        raise NotImplementedError

    def add_role(self, kind, agent, name):
        role = kind(self.model)
        role.setup()
        role.name = name
        role.space = self
        role.agent = agent
        agent.roles[name] = role
        self.graph.add_node(role)
        return role

    def remove_role(self, role):
        name = role.name
        agent = role.agent
        agent.roles.pop(name)
        self.graph.remove_node(role)


class EcoAccount(Object):

    def setup(self):
        super().setup()
        self.agent = None
        self.stocks = {
            "deposits": 0,
            "loans": 0,
            "inventories": 0,
            "bonds": 0,
            "cash": 0,
            "advances": 0,
            "equities": 0,
        }
        self.flows = {
            "consumption": 0,
            "wages": 0,
            "public_transfers": 0,
            "taxes": 0,
            "dep_interests": 0,
            "loan_interests": 0,
            "bond_interests": 0,
            "cash_interests": 0,
            "adv_interests": 0,
            "dividends": 0,
            "profit_transfers": 0,
        }

    def debit_stock(self, name, amount):
        self.stocks[name] = self.stocks.get(name, 0) - amount

    def credit_stock(self, name, amount):
        self.stocks[name] = self.stocks.get(name, 0) + amount

    def debit_flow(self, name, amount):
        self.flows[name] = self.flows.get(name, 0) - amount

    def credit_flow(self, name, amount):
        self.flows[name] = self.flows.get(name, 0) + amount

    def clear_flows(self):
        self.flows.clear()
