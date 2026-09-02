
from agentpy import Agent
from agentpy.objects import Object
from networkx import Graph


class EcoAgent(Agent):
    """
    Classe de base des agents économiques.

    Un agent possède un ensemble de rôles.
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.roles = {}


class EcoRole:
    """
    Classe de base des rôles économiques.

    Un rôle est un proxy de l'agent propriétaire
    et un adaptateur vers un espace d'interaction.
    """

    name = ''

    def __init__(self, agent, space):
        super().__init__()
        self.agent = agent
        self.space = space



class EcoSpace(Object):
    """
    Classe de base des espaces d'interaction.

    Un espace contient des rôles qui correspondent
    à ses noeuds.
    """

    def setup(self):
        self.roles = {}
        self.graph = Graph()


    def add_role(self, kind, agent, name):
        role = kind(agent, self)
        agent.roles[name] = role  
        self.graph.add_node(role)   
        return role

    def remove_role(self, role):
        name = role.name
        print(name, role.agent.roles)
        agent = role.agent
        agent.roles.pop(name)
        self.graph.remove_node(role)



