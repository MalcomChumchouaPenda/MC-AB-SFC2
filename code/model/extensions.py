import re
from agentpy import Agent, Network, AgentNode
from agentpy import AgentList, AgentIter, AttrDict
from model.accounts import FINANCIAL_ASSETS, REAL_ASSETS, TRANSACTIONS


def camel_to_snake(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()



class EcoAgent(Agent):
    """
    Classe de base des agents économiques.

    Un agent possède un ensemble de rôles.
    """

    def setup(self):
        self.roles = {}
        self.country_pos = 0
        self.account = None


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
        self.prefix = ""
        self.name = camel_to_snake(self.__class__.__name__)

    @property
    def id(self):
        return self.agent.id


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
        self.roles = {}
        self.spaces = {}
        self.accounts = {}

    #
    # Agent management
    #
    def add_agents(self, agents):
        cls_name = agents[0].__class__.__qualname__
        kind_name = camel_to_snake(cls_name)
        method_name = "add_" + kind_name
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            for agent in agents:
                method(agent)

    #
    # Role management
    #
    def add_role(self, kind, agent, prefix=""):
        role = kind(agent, self)
        role.prefix = prefix
        key = role.name
        if prefix:
            key = prefix + "_" + key
        agent.roles[key] = role
        self.roles[agent.id] = role
        self.positions[agent] = role
        self.graph.add_node(role)
        if agent.account is None:
            self.add_account(agent)
        return role

    def remove_role(self, role):
        key = role.name
        prefix = role.prefix
        if prefix:
            key = prefix + "_" + key
        agent = role.agent
        agent.roles.pop(key)
        self.roles.pop(agent.id)
        self.positions.pop(agent)
        self.graph.remove_node(role)
        if self.env is None:
            self.remove_account(agent)

    def find_all_roles(self, pattern):
        selected = [role for role in self.roles.values() if pattern in role.name]
        return AgentList(self.model, selected)

    def find_random_roles(self, pattern, size):
        found = self.find_all_roles(pattern)
        selected = found.random(n=min(size, len(found)))
        return selected.to_list()

    #
    # Links/neighbors management
    #

    def neighbors(self, role):
        edges = self.graph.edges(role)
        neighbors = [neighbor for _, neighbor in edges]
        return AgentIter(self.model, neighbors)

    def links(self, role, neighbor_name):
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

    def remove_account(self, agent):
        agent.account = None
        self.accounts.pop(agent.id)

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
        subspace = kind(self.model, **kwargs)
        subspace.env = self
        self.spaces[name] = subspace
        return subspace

    def evolve(self):
        for subspace in self.spaces.values():
            subspace.update_state()
            subspace.clear_defaults()
        self.update_state()
        self.clear_defaults()

    def update_state(self):
        raise NotImplementedError

    def clear_defaults(self):
        raise NotImplementedError
