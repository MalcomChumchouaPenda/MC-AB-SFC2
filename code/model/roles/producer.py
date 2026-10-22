import math
from model.extensions import EcoRole


class Producer(EcoRole):

    def __init__(self, agent, env, prefix=""):
        super().__init__(agent, env, prefix=prefix)
        self.defaulted = False
        self.variety = None
        self.output = 0
        self.sales = 0
        self.price = 0
        self.rd = 0
        self.phi = 0
        self.inventories = 0

    #
    # Perceptions
    #
    def get_average_price(self):
        return self.env.average_price

    def get_average_phi(self):
        return self.env.average_prod

    #
    # Actions
    #
    def produce_goods(self, labor):
        self.output = self.phi * labor
        self.inventories += self.output

    def execute_rd(self, rd):
        self.rd = rd
        random = self.env.model.nprandom
        prob = self._calc_rd_success_probability()
        success = random.choice([0, 1], p=[1 - prob, prob])
        if success:
            self._innovate()
            self._imitate()

    def _calc_rd_success_probability(self):
        env = self.env
        avg_price = env.average_price
        avg_prod = env.average_prod
        prob = 1 - math.exp(-env.p.nu * self.rd / (avg_price * avg_prod))
        return prob

    def _innovate(self):
        env = self.env
        delta = env.p.delta
        random = env.model.nprandom
        self.phi *= 1 + random.uniform(0, delta)

    def _imitate(self):
        env = self.env
        random = env.model.nprandom
        avg_prod = env.average_prod
        prod_diff = avg_prod - self.phi
        if prod_diff > 0:
            self.phi += random.uniform(0, prod_diff)
