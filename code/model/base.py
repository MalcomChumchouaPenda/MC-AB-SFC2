from collections import defaultdict
from agentpy import Agent, Network, AgentNode, AgentDList, AttrDict
from model.accounts import FINANCIAL_ASSETS, REAL_ASSETS, TRANSACTIONS


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
        self.group = ""

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


class EcoAccount(AttrDict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in FINANCIAL_ASSETS + REAL_ASSETS + TRANSACTIONS:
            self[name] = 0.0

    def clear_flows(self):
        for name in TRANSACTIONS:
            self[name] = 0


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
        self.roles = AgentDList(self.model)

    #
    # Role management
    #
    def add_role(self, kind, agent, group):
        name = group
        role = kind(agent, self)
        role.name = name
        role.group = group
        agent.roles[name] = role
        if agent.account is None:
            self.add_account(agent)
        self.roles.append(role)
        self.positions[agent] = role
        self.graph.add_node(role)
        return role

    def remove_role(self, role):
        name = role.name
        agent = role.agent
        agent.roles.pop(name)
        self.roles.remove(role)
        self.graph.remove_node(role)

    def find_all_roles(self, group):
        roles = self.roles
        return roles.select(roles.group == group)

    def find_random_roles(self, group, size):
        roles = self.roles
        found = roles.select(roles.group == group)
        selected = found.random(n=min(size, len(found)))
        return selected.to_list()

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
        return self.accounts[account_id][category]

    def transfer_stock(self, category, source, target, amount):
        if self.env is not None:
            self.env.transfer_stock(category, source, target, amount)
        else:
            self.accounts[source][category] -= amount
            self.accounts[target][category] += amount

    def make_transaction(self, category, source, target, amount):
        if self.env is not None:
            self.env.make_transaction(category, source, target, amount)
        else:
            self.accounts[source][category] -= amount
            self.accounts[target][category] += amount

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
