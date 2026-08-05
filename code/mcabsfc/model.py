import agentpy as ap


class EcoModel(ap.Model):
    """
    Classe de base du modèle économique.

    Responsable de l'orchestration de la simulation.
    """

    def __init__(self, parameters=None, _run_id=None, **kwargs):
        super().__init__(parameters, _run_id, **kwargs)
        self.agents = {}
        self.spaces = {}
