from ..base import EcoSpace
from ..roles import UnionCentralBankRole


class MonetaryUnionSpace(EcoSpace):

    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self._discount_rate = 0.0
        self.average_inflation = 0
        self.central_bank_role = None
        self.countries = {}
        self.markets = {}

    @property
    def discount_rate(self):
        return self._discount_rate

    @discount_rate.setter
    def discount_rate(self, rate):
        self._discount_rate = rate
        for country in self.countries.values():
            country.discount_rate = rate

    def add_central_bank(self, central_bank):
        cb_role = self.add_role(UnionCentralBankRole, central_bank, "central_bank")
        self.central_bank_role = cb_role
        return cb_role

    def calc_average_inflation(self):
        countries = self.countries
        countries_gdps = [c.gdp for c in countries.values()]
        weighted_inflations = [c.gdp * c.inflation for c in countries.values()]
        return sum(weighted_inflations) / sum(countries_gdps)

    def update_statistics(self):
        for country in self.countries.values():
            country.update_statistics()
        self.average_inflation = self.calc_average_inflation()
