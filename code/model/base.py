from collections import defaultdict
from agentpy import Agent, Network, AgentNode, AgentDList
from model.constants import STOCK_NAMES, FLOW_NAMES


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
        self.stocks = {name: 0.0 for name in STOCK_NAMES}
        self.flows = {name: 0.0 for name in FLOW_NAMES}

    #
    # stocks accounting
    #
    def incr_stock(self, name, amount):
        self.stocks[name] += amount

    def decr_stock(self, name, amount):
        self.stocks[name] -= amount

    #
    # flows accounting
    #
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
        self.env = None
        self.spaces = {}
        self.accounts = {}
        self.roles = defaultdict(lambda: AgentDList(self.model))

    #
    # Role management
    #
    def add_role(self, kind, agent, name):
        role = kind(agent, self)
        role.name = name
        agent.roles[name] = role
        if agent.account is None:
            self.add_account(agent)
        self.roles[name].append(role)
        self.positions[agent] = role
        self.graph.add_node(role)
        return role

    def remove_role(self, role):
        name = role.name
        agent = role.agent
        agent.roles.pop(name)
        self.roles[name].remove(role)
        self.graph.remove_node(role)

    def find_all_roles(self, name):
        return AgentDList(self.model, self.roles[name])

    def find_one_role(self, name):
        return self.roles[name][0]

    def find_random_role(self, name, size):
        roles = self.roles[name]
        min_size = min(size, len(roles))
        return roles.random(n=min_size).to_dlist()

    #
    # Links/neighbors management
    #

    def find_neighbors(self, role):
        edges = self.graph.edges(role)
        neighbors = [neighbor for _, neighbor in edges]
        return AgentDList(self.model, neighbors)

    def find_links(self, role, neighbor_name):
        links = []
        edges = self.graph.edges(role, data=True)
        for _, neighbor, data in edges:
            link = {neighbor_name: neighbor}
            link.update(data)
            links.append(link)
        return links

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

    def get_stock(self, category, account_id):
        if self.env is not None:
            return self.env.get_stock(category, account_id)
        return self.accounts[account_id].stocks[category]

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
