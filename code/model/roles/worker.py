from model.base import EcoRole


class Worker(EcoRole):

    def setup(self):
        super().setup()
        self.labor_supply = 1.0

    #
    # perceptions method
    #

    @property
    def labor_sold(self):
        return 1.0 - self.labor_supply

    def get_unemployment(self):
        return self.space.unemployment

    #
    # actions method
    #
    
    def find_employers(self, psi):
        return self.space.find_employers(psi)

    def accept_job(self, employer, quantity):
        self.space.hire_worker(self, employer, quantity)
