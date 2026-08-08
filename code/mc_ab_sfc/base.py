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

    def __init__(self, owner, space):
        super().__init__(owner.id)
        self.owner = owner
        self.space = space

    def increase_stock(self, stock_name, amount):
        owner = self.owner
        value = getattr(owner, stock_name)
        setattr(owner, stock_name, value + amount)

    def decrease_stock(self, stock_name, amount):
        owner = self.owner
        value = getattr(owner, stock_name)
        setattr(owner, stock_name, value - amount)

    def clear_stock(self, stock_name):
        owner = self.owner
        getattr(owner, stock_name)
        setattr(owner, stock_name, 0)

    def increase_flow(self, flow_name, amount):
        owner = self.owner
        value = getattr(owner, flow_name)
        setattr(owner, flow_name, value + amount)

    def decrease_flow(self, flow_name, amount):
        owner = self.owner
        value = getattr(owner, flow_name)
        setattr(owner, flow_name, value - amount)

    def clear_flow(self, flow_name):
        owner = self.owner
        getattr(owner, flow_name)
        setattr(owner, flow_name, 0)


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
