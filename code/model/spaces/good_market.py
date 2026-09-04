from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.consumer import Consumer
from model.roles.producer import Producer


class GoodsMarket(EcoSpace):

    def setup(self):
        super().setup()

        # state
        self.tradable = False
        self.average_price_prev = 0
        self.average_price = 0
        self.average_prod = 0

        # roles set
        self.consumers = AgentDList(self.model)
        self.producers = AgentDList(self.model)

    #
    # Roles management
    #
    def add_producer(self, firm):
        role = self.add_role(Producer, firm, "producer")
        self.producers.append(role)
        return role

    def add_consumer(self, household):
        name = "trad_consumer" if self.tradable else "non_trad_consumer"
        role = self.add_role(Consumer, household, name)
        self.consumers.append(role)
        return role

    #
    # Reactions
    #
    def find_suppliers(self, psi):
        producers = self.producers
        return producers.random(min(psi, len(producers)))

    def buy_goods(self, consumer, producer, quantity):
        producer.inventories -= quantity
        amount = quantity * producer.price
        producer.credit_flow("consumption", amount)
        producer.credit_stock("cash", amount)
        consumer.debit_flow("consumption", amount)
        consumer.debit_stock("cash", amount)

    #
    #   Evolution
    #
    def update_state(self):
        producers = self.producers
        self.average_price_prev = self.average_price
        self.average_price = sum(producers.price) / max(1, len(producers))
        self.average_prod = sum(producers.productivity) / max(1, len(producers))

    def calc_inflation(self):
        prev_price = self.average_price_prev
        current_price = self.average_price
        return (current_price - prev_price) / prev_price

    def calc_gdp(self):
        return sum(prod.account.stocks.get("consumption", 0) for prod in self.producers)
