import pytest
from model.spaces.monetary_union import MonetaryUnion
from model.agents.household import Household
from model.agents.firm import Firm


@pytest.fixture
def model(fake_model, make_dlist):
    # Given
    model = fake_model
    model.p.cT = 0.6
    model.p.eta = 0.3
    model.p.initial_equity = 400
    model.p.initial_tax_rate = 0.0
    model.p.initial_phi = 1.0
    model.p.initial_discount_rate = 0.0
    model.p.initial_wage = 1.0
    model.p.omega = 0.1
    model.p.psi = 5
    model.p.sigma = 4
    model.firms = make_dlist()
    model.banks = make_dlist()
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.create_markets()
    union.create_countries(1)
    model.union = union
    return union


@pytest.fixture
def country(union):
    country = union.spaces["country_0"]
    return country


@pytest.fixture
def founders(model, union):
    # Given
    founders = []
    for i in range(2):
        household = Household(model)
        household.desired_equity = 300 - i * 100
        union.add_agents([household])
        founders.append(household)
    return founders


@pytest.fixture
def before_firm_creation(founders):
    # Given
    for household in founders:
        household.account["cash"] = 400
        citizen_role = household.roles["citizen"]
        citizen_role.resid_equity = household.desired_equity


@pytest.mark.usefixtures("before_firm_creation")
def test_appends_new_firm_to_model(founders, model):
    # Given
    initiator = founders[0]
    firms = model.firms

    # When
    initiator.invest_equity()

    # Then
    assert len(firms) == 1
    assert isinstance(firms[0], Firm)


@pytest.mark.usefixtures("before_firm_creation")
def test_increases_new_firm_equities(founders, model):
    # Given
    initiator, partner = founders
    firms = model.firms

    # When
    initiator.invest_equity()

    # Then
    assert initiator.account["equities"] == 300
    assert partner.account["equities"] == 200
    assert firms[0].account["equities"] == -500


@pytest.mark.usefixtures("before_firm_creation")
def test_transfers_cash_from_households_to_firm(founders, model):
    # Given
    initiator, partner = founders
    firms = model.firms

    # When
    initiator.invest_equity()

    # Then
    assert initiator.account["cash"] == 100
    assert partner.account["cash"] == 200
    assert firms[0].account["cash"] == 500


@pytest.mark.usefixtures("before_firm_creation")
def test_adds_new_firm_equity_links_to_graph(country, founders, model):
    # Given
    initiator, partner = founders
    citizen1 = initiator.roles["citizen"]
    citizen2 = partner.roles["citizen"]
    firms = model.firms
    positions = country.positions

    # When
    initiator.invest_equity()

    # Then
    assert country.graph[citizen1][positions[firms[0]]]["value"] == 300
    assert country.graph[citizen2][positions[firms[0]]]["value"] == 200
