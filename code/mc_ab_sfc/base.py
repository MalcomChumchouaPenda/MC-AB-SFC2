import agentpy as ap
from networkx import DiGraph


class EcoAgent(ap.Agent):
    """
    Classe de base des agents économiques.

    Un agent possède un ensemble de rôles.
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.roles = {}

    def update_history(self):
        pass


class EcoRole(ap.AgentNode):
    """
    Classe de base des rôles économiques.

    Un rôle est un proxy de l'agent propriétaire
    et un adaptateur vers un espace d'interaction.
    """

    def __init__(self, agent, space):
        super().__init__(agent.id)
        self.agent = agent
        self.space = space

    def increase_stock(self, stock_name, amount):
        agent = self.agent
        value = getattr(agent, stock_name)
        setattr(agent, stock_name, value + amount)

    def decrease_stock(self, stock_name, amount):
        agent = self.agent
        value = getattr(agent, stock_name)
        setattr(agent, stock_name, value - amount)

    def clear_stock(self, stock_name):
        agent = self.agent
        getattr(agent, stock_name)
        setattr(agent, stock_name, 0)

    def increase_flow(self, flow_name, amount):
        agent = self.agent
        value = getattr(agent, flow_name)
        setattr(agent, flow_name, value + amount)

    def decrease_flow(self, flow_name, amount):
        agent = self.agent
        value = getattr(agent, flow_name)
        setattr(agent, flow_name, value - amount)

    def clear_flow(self, flow_name):
        agent = self.agent
        getattr(agent, flow_name)
        setattr(agent, flow_name, 0)


class EcoSpace(ap.Network):
    """
    Classe de base des espaces d'interaction.

    Un espace contient des rôles qui correspondent
    à ses noeuds.
    """

    def __init__(self, model, **kwargs):
        super().__init__(model, graph=DiGraph(), **kwargs)
        self.roles = {}

    def add_role(self, kind, agent, key):
        role = kind(agent, self)
        agent.roles[key] = role
        self.graph.add_node(role)
        return role
