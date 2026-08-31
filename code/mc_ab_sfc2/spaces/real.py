from ..base import EcoSpace
from ..roles.real import EmployerRole, WorkerRole, ConsumerRole, ProducerRole


class GoodsMarket(EcoSpace):

    def __init__(self, model, tradable=True, **kwargs):
        super().__init__(model, **kwargs)
        self.tradable = tradable
        self.gdp = 0
        self.inflation = 0.0
        self.average_price = 0
        self.average_productivity = 0

    def add_supplier(self, firm):
        return self.add_role(ProducerRole, firm, "producer")

    def add_consumer(self, household):
        key = "consumer_tradable" if self.tradable else "consumer_non_tradable"
        return self.add_role(ConsumerRole, household, key)

    def search_suppliers(self, psi):
        suppliers = [n for n in self.nodes if isinstance(n, ProducerRole)]
        return self.model.random.sample(suppliers, k=min(psi, len(suppliers)))

    def buy_goods(self, consumer, producer, quantity):
        amount = quantity * producer.price
        producer.decrease_stock("inventories", quantity)
        producer.increase_stock("cash", amount)
        producer.increase_flow("sales", amount)
        consumer.decrease_stock("cash", amount)
        if self.tradable:
            consumer.increase_flow("tradable_cons", amount)
        else:
            consumer.increase_flow("non_tradable_cons", amount)

    def update_statistics(self):
        nodes = self.graph.nodes  # roles
        producers = [n for n in nodes if isinstance(n, ProducerRole)]
        self.gdp = self.calc_gdp(producers)
        self.inflation = self.calc_inflation(producers)
        self.average_price = self.calc_average_price(producers)
        self.average_productivity = self.calc_average_productivity(producers)

    def calc_inflation(self, producers):
        prev_price = self.average_price
        current_price = self.calc_average_price(producers)
        if prev_price <= 0:
            return 0
        return (current_price - prev_price) / prev_price

    def calc_average_price(self, producers):
        return sum(prod.price for prod in producers) / max(1, len(producers))

    def calc_average_productivity(self, producers):
        return sum(prod.productivity for prod in producers) / max(1, len(producers))

    def calc_gdp(self, producers):
        return sum(prod.sales for prod in producers)


class LaborMarket(EcoSpace):

    def setup(self):
        self.average_wage = 0

    def add_employer(self, firm):
        return self.add_role(EmployerRole, firm, "employer")

    def add_worker(self, household):
        return self.add_role(WorkerRole, household, "worker")

    def create_job(self, worker, employer, quantity):
        wage = employer.wage_offer
        employer.labor_demand -= quantity
        self.graph.add_edge(worker, employer, wage=wage, quantity=quantity)

    def search_employers(self, psi):
        employers = [n for n in self.nodes if isinstance(n, EmployerRole)]
        return self.model.random.sample(employers, k=min(psi, len(employers)))

    def get_labor_sold(self, worker):
        edges = self.graph.edges  # contracts
        return sum(data["quantity"] for (w, e), data in edges.items() if w == worker)

    def update_statistics(self):
        nodes = self.graph.nodes  # roles
        employers = [n for n in nodes if isinstance(n, EmployerRole)]
        self.average_wage = self.calc_average_wage(employers)

    def calc_average_wage(self, employers):
        return sum([e.wage_offer for e in employers]) / max(1, len(employers))
