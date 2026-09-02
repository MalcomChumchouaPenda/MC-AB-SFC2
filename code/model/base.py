
from agentpy import Agent
from agentpy.objects import Object
from networkx import Graph


class EcoAgent(Agent):
    """
    Classe de base des agents économiques.

    Un agent possède un ensemble de rôles.
    """

    def setup(self):
        self.roles = {}


class EcoRole(Object):
    """
    Classe de base des rôles économiques.

    Un rôle est un proxy de l'agent propriétaire
    et un adaptateur vers un espace d'interaction.
    """

    def setup(self):
        self.name = ''
        self.agent = None
        self.space = None



class EcoSpace(Object):
    """
    Classe de base des espaces d'interaction.

    Un espace contient des rôles qui correspondent
    à ses noeuds.
    """

    def setup(self):
        self.roles = {}
        self.graph = Graph()


    def add_role(self, kind, agent):
        role = kind(self.model)
        role.setup()
        role.space = self
        role.agent = agent
        agent.roles[role.name] = role  
        self.graph.add_node(role)   
        return role

    def remove_role(self, role):
        name = role.name
        agent = role.agent
        agent.roles.pop(name)
        role.space = None
        role.agent = None
        self.graph.remove_node(role)



