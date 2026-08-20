from ..base import EcoRole


class CommercialBankRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.central_bank = None

    def get_discount_rate(self):
        return self.space.discount_rate

    def request_cash_advances(self, amount):
        self.space.request_cash_advances(self, amount)
