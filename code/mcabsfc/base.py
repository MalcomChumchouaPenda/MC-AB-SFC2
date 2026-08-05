import agentpy as ap


class EcoAgent(ap.Agent):
    """
    Classe de base des agents économiques.

    Un agent possède un ensemble de rôles.
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.roles = {}


class EcoRole(ap.AgentNode):
    """
    Classe de base des rôles économiques.

    Un rôle est un proxy de l'agent propriétaire
    et un adaptateur vers un espace d'interaction.
    """

    def __init__(self, owner):
        super().__init__(owner.id)
        self.owner = owner
        self.space = None


class EcoSpace(ap.Network):
    """
    Classe de base des espaces d'interaction.

    Un espace contient des rôles qui correspondent
    à ses noeuds.
    """

    def __init__(self, model, graph=None, **kwargs):
        super().__init__(model, graph, **kwargs)
        self.roles = {}

