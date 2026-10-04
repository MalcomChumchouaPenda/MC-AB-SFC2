from model.extensions import EcoSpace
from model.roles.consumer import Consumer
from model.roles.producer import Producer


class GoodsMarket(EcoSpace):

    def setup(self, tradable=False):
        super().setup()
        self.tradable = tradable
        self.average_price_prev = 0
        self.average_price = 0
        self.average_prod = 0

    #
    # Roles management
    #

    def place_household(self, household):
        group = "trad_consumer" if self.tradable else "non_trad_consumer"
        role = self.add_role(Consumer, household, group)
        role.preference = household.preference

    def place_firm(self, firm):
        role = self.add_role(Producer, firm, "producer")
        role.variety = firm.variety

    #
    # Reactions
    #
    def buy_goods(self, consumer, producer, quantity):
        producer.inventories -= quantity
        amount = quantity * producer.price
        self.transfer_stock("cash", consumer.id, producer.id, amount)
        self.make_transaction("consumption", consumer.id, producer.id, amount)

    #
    #   Evolution
    #
    def update_state(self):
        roles = self.roles
        producers = roles.select(roles.name == "producer")
        self.average_price_prev = self.average_price
        self.average_price = sum(producers.price) / max(1, len(producers))
        self.average_prod = sum(producers.productivity) / max(1, len(producers))

    def calc_inflation(self):
        prev_price = self.average_price_prev
        current_price = self.average_price
        return (current_price - prev_price) / prev_price

    def calc_gdp(self):
        roles = self.roles
        producers = roles.select(roles.name == "producer")
        return sum(self.get_stock("consumption", i) for i in producers.id)
