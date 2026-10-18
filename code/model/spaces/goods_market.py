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

    def add_household(self, household):
        prefix = "trad" if self.tradable else "non_trad"
        self.add_role(Consumer, household, prefix=prefix)

    def add_firm(self, firm):
        if firm.tradable == self.tradable:
            self.add_role(Producer, firm)

    #
    # Reactions
    #
    def buy_goods(self, consumer, producer, quantity):
        amount = quantity * producer.price
        producer.inventories -= quantity
        producer.sales += amount
        self.transfer_stock("cash", consumer.id, producer.id, amount)
        self.make_transaction("consumption", consumer.id, producer.id, amount)

    #
    # statistics
    #

    def calc_inflation(self):
        prev_price = self.average_price_prev
        if prev_price == 0:
            return 0
        current_price = self.average_price
        return (current_price - prev_price) / prev_price

    def calc_gdp(self):
        producers = self.find_all_roles("producer")
        return sum(self.get_stock("consumption", i) for i in producers.id)

    def calc_productivity_range(self):
        producers = self.find_all_roles("producer")
        if len(producers) == 0:
            return None
        values = producers.productivity
        return min(values), max(values)

    def calc_price_range(self):
        producers = self.find_all_roles("producer")
        if len(producers) == 0:
            return None
        values = producers.price
        return min(values), max(values)

    def calc_sales_range(self):
        producers = self.find_all_roles("producer")
        if len(producers) == 0:
            return None
        values = producers.sales
        return min(values), max(values)

    #
    #   Evolution
    #
    def update_state(self):
        producers = self.find_all_roles("producer")
        self.average_price_prev = self.average_price
        self.average_price = sum(producers.price) / max(1, len(producers))
        self.average_prod = sum(producers.productivity) / max(1, len(producers))

    def clear_defaults(self):
        roles = self.find_all_roles("producer")
        for role in roles.select(roles.defaulted == True):
            self.remove_role(role)

    def clear_transactions(self):
        super().clear_transactions()
        for role in self.find_all_roles("producer"):
            role.sales = 0
