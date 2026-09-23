from agentpy import Agent, Network, AgentNode, AttrDict


class EcoAgent(Agent):
    """
    Classe de base des agents économiques.

    Un agent possède un ensemble de rôles.
    """

    def setup(self):
        self.roles = {}
        self.country_id = 0
        self.account = None
        self.cb_id = None
        self.bank_id = None


class EcoRole(AgentNode):
    """
    Classe de base des rôles économiques.

    Un rôle est un proxy de l'agent propriétaire
    et un adaptateur vers un espace d'interaction.
    """

    def __init__(self, agent, env):
        super().__init__(label=agent.id)
        self.agent = agent
        self.env = env
        self.name = ""

    @property
    def country_id(self):
        return self.agent.country_id

    @property
    def id(self):
        return self.agent.id

    @property
    def cb_id(self):
        return self.agent.cb_id

    @property
    def bank_id(self):
        return self.agent.bank_id

    @bank_id.setter
    def bank_id(self, account):
        self.agent.bank_id = account


class EcoAccount:

    def __init__(self):
        super().__init__()
        self.stocks = {
            "deposits": 0.0,
            "loans": 0.0,
            "inventories": 0.0,
            "bonds": 0.0,
            "cash": 0.0,
            "advances": 0.0,
            "equities": 0.0,
        }
        self.flows = {
            "consumption": 0.0,
            "wages": 0.0,
            "public_transfers": 0.0,
            "taxes": 0.0,
            "dep_interests": 0.0,
            "loan_interests": 0.0,
            "loan_defaults": 0.0,
            "bond_interests": 0.0,
            "cash_interests": 0.0,
            "adv_interests": 0.0,
            "dividends": 0.0,
            "profit_transfers": 0.0,
        }


    def incr_stock(self, name, amount):
        self.stocks[name] += amount

    def decr_stock(self, name, amount):
        self.stocks[name] -= amount


    def incr_flow(self, name, amount):
        self.flows[name] += amount
        
    def decr_flow(self, name, amount):
        self.flows[name] -= amount

    def clear_flows(self):
        flows = self.flows
        for name in flows.keys():
            flows[name] = 0


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
        role = kind(agent, self)
        role.name = name
        agent.roles[name] = role
        self.graph.add_node(role)
        self.positions[agent] = role
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

    def transfer_stock(self, category, source, target, amount):
        if self.env is not None:
            self.env.transfer_stock(category, source, target, amount)
        else:
            self.accounts[source].decr_stock(category, amount)
            self.accounts[target].incr_stock(category, amount)

    def record_flow(self, category, source, target, amount):
        if self.env is not None:
            self.env.record_flow(category, source, target, amount)
        else:
            self.accounts[source].decr_flow(category, amount)
            self.accounts[target].incr_flow(category, amount)

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
