from agentpy import Agent, Network, AgentDList, AttrDict
from agentpy.objects import Object


class EcoAgent(Agent):
    """
    Classe de base des agents économiques.

    Un agent possède un ensemble de rôles.
    """

    def setup(self):
        self.roles = {}
        self.country_id = 0
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
        self.env = None
        self.name = ""

    @property
    def country_id(self):
        return self.agent.country_id

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


class EcoAccount(AttrDict):

    STOCK_NAMES = (
        "deposits",
        "loans",
        "inventories",
        "bonds",
        "cash",
        "advances",
        "equities",

    )

    FLOW_NAMES = (
        "consumption",
        "wages",
        "public_transfers",
        "taxes",
        "dep_interests",
        "loan_interests",
        "loan_defaults",
        "bond_interests",
        "cash_interests",
        "adv_interests",
        "dividends",
        "profit_transfers",

    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.STOCK_NAMES + self.FLOW_NAMES:
            self[name] = 0


    def debit(self, name, amount):
        self[name] -= amount

    def credit(self, name, amount):
        self[name] += amount


    def clear_flows(self):
        for name in self.FLOW_NAMES:
            self[name] = 0


class EcoSpace(Network):
    """
    Classe de base des espaces d'interaction.

    Un espace contient des rôles qui correspondent
    à ses noeuds.
    """

    def setup(self):
        self.roles = {}
        self.env = None
        self.spaces = {}
        self.accounts = {}


    #
    # Role management
    #
    def add_role(self, kind, agent, name):
        role = kind(self.model)
        role.setup()
        role.name = name
        role.env = self
        role.agent = agent
        agent.roles[name] = role
        self.graph.add_node(role)
        return role

    def remove_role(self, role):
        name = role.name
        agent = role.agent
        agent.roles.pop(name)
        self.graph.remove_node(role)

    #
    # Account management
    #
    def add_account(self, agent):
        if self.env is not None:
            return self.env.add_account(agent)
        account = EcoAccount()
        agent.account = account
        self.accounts[agent.id] = account
        return account


    def transfer(self, item, source, target, amount):
        if self.env is not None:
            self.env.transfer(item, source, target, amount)
        self.accounts[source].debit(item, amount)
        self.accounts[target].credit(item, amount)


    #
    # Space management
    #
    def add_space(self, kind, name, **kwargs):
        sub_space = kind(self.model, **kwargs)
        sub_space.env = self
        self.spaces[name] = sub_space
        return sub_space

    def evolve(self):
        for sub_space in self.spaces.values():
            sub_space.update_state()
            sub_space.clear_defaults()
        self.update_state()
        self.clear_defaults()

    def update_state(self):
        raise NotImplementedError

    def clear_defaults(self):
        raise NotImplementedError
