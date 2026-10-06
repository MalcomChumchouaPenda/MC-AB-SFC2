import pytest
from model.agents.firm import Firm
from model.agents.household import Household
from model.spaces.country import Country


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.initial_wage = 0.0
    model.p.theta = 0.20
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.create_markets()
    return country


@pytest.fixture
def firm(model, country):
    # Given
    firm = Firm(model)
    firm.country_pos = country.pos
    country.add_firm(firm)
    return firm


def test_production_planning_pipeline(firm):
    # Given
    firm.expected_sales = 150
    firm.roles["producer"].inventories = 30
    firm.roles["producer"].productivity = 3

    # When
    firm.plan_production()

    # Then
    assert firm.desired_output == 150
    assert firm.desired_labor == 50


@pytest.fixture
def workers(model, country, firm):
    # Given
    workers = []
    employer = firm.roles["employer"]
    market = country.spaces["labor_market"]
    for _ in range(5):
        household = Household(model)
        country.add_household(household)
        worker = household.roles["worker"]
        workers.append(worker)
        market.hire_worker(worker, employer, 1.0)
    return workers


@pytest.mark.usefixtures("workers")
def test_updates_producer_inventories(firm):
    # Given
    producer = firm.roles["producer"]
    producer.productivity = 2.0

    # When
    firm.produce_goods()

    # Then
    assert producer.inventories == 10.0
