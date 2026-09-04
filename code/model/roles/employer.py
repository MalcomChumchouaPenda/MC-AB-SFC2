from model.base import EcoRole


class Employer(EcoRole):

    def setup(self):
        super().setup()
        self.wage = 0
        self.labor_demand = 0

    #
    # perceptions method
    #
    def get_unemployment(self):
        return self.space.unemployment

    def get_jobs(self):
        return self.space.find_jobs(self)
    
