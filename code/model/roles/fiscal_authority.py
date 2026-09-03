from model.base import EcoRole


class FiscalAuthority(EcoRole):

    @property
    def tax_rate(self):
        return self.space.tax_rate

    @tax_rate.setter
    def tax_rate(self, rate):
        self.space.tax_rate = rate