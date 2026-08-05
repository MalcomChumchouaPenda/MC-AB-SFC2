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

    def __init__(self, owner, space):
        super().__init__(owner.id)
        self.owner = owner
        self.space = space

    def credit_stock(self, stock_name, amount):
        owner = self.owner
        value = getattr(owner, stock_name)
        setattr(owner, stock_name, value + amount)

    def debit_stock(self, stock_name, amount):
        owner = self.owner
        value = getattr(owner, stock_name)
        setattr(owner, stock_name, value - amount)

    def credit_flow(self, flow_name, amount):
        owner = self.owner
        value = getattr(owner, flow_name)
        setattr(owner, flow_name, value + amount)

    def debit_flow(self, flow_name, amount):
        owner = self.owner
        value = getattr(owner, flow_name)
        setattr(owner, flow_name, value - amount)


class EcoSpace(ap.Network):
    """
    Classe de base des espaces d'interaction.

    Un espace contient des rôles qui correspondent
    à ses noeuds.
    """

    def __init__(self, model, graph=None, **kwargs):
        super().__init__(model, graph, **kwargs)
        self.roles = {}
