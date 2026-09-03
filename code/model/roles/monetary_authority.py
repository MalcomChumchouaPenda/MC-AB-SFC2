from model.base import EcoRole


class MonetaryAuthority(EcoRole):

    @property
    def discount_rate(self):
        return self.space.discount_rate

    @discount_rate.setter
    def discount_rate(self, rate):
        self.space.discount_rate = rate
