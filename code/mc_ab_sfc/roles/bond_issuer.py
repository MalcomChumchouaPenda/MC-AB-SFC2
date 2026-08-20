from ..base import EcoRole


class BondIssuerRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.bond_supply = 0

    @property
    def bond_rate(self):
        return self.agent.bond_rate

    @property
    def bonds(self):
        return self.agent.bonds

    @property
    def gdp(self):
        return self.agent.gdp

    def issue_bonds(self, amount):
        self.bond_supply = amount

    def pay_bond_debt(self):
        self.space.pay_bond_debt(self)
