
from agentpy import Agent
from agentpy.objects import Object
from networkx import DiGraph


class EcoAgent(Agent):
    """
    Classe de base des agents économiques.

    Un agent possède un ensemble de rôles.
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.roles = {}


class EcoRole(Object):
    """
    Classe de base des rôles économiques.

    Un rôle est un proxy de l'agent propriétaire
    et un adaptateur vers un espace d'interaction.
    """

    def __init__(self, model, agent_id, space):
        super().__init__(model)
        self.agent_id = agent_id
        self.space = space



class EcoSpace(Object):
    """
    Classe de base des espaces d'interaction.

    Un espace contient des rôles qui correspondent
    à ses noeuds.
    """

    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.roles = {}

    def add_role(self, kind, agent, key):
        role = kind(self.model, agent.id, self)
        agent.roles[key] = role
        return role


class EcoStock(Object):
    pass

