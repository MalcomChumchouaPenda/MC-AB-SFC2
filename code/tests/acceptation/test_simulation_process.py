import pytest
from model.model import EcoModel


@pytest.fixture
def params():
    return {
        "country_number": 2,
        "household_number": 10,
        "psi": 10,
        "upsilon": 1.0,
        "initial_wage": 1.0,
        "initial_productivity": 1.0,
        "initial_tax_rate": 0.4,
        "cy": 0.9,
        "cd": 0.2,
        "delta": 0.03,
        "cT": 0.4,
        "beta": 2.0,
        "lambda_": 0.2,
        "theta": 0.2,
        "gamma": 0.03,
        "nu": 1.5,
        "rho": 0.95,
        "zeta": 0.1,
        "mu1": 20,
        "mu2": 0.1,
        "iota_l": 1.0,
        "chi": 0.003,
        "iota_b": 0.1,
        "initial_discount_rate": 0.0,
        "initial_bond_rate": 0.001,
        "long_run_rate": 0.0075,
        "xi": 0.8,
        "xi_deltap": 2,
        "inflation_target": 0.005,
        "dmax": 0.03,
        "tax_min": 0.35,
        "tax_max": 0.45,
        "g_min": 0.4,
        "g_max": 0.6,
        "eta": 0.03,
        "initial_equity": 10.0,
    }


def test_create_initial_population(params):
    # Given
    params["steps"] = 0
    params["household_number"] = 5
    params["country_number"] = 2
    model = EcoModel(params)

    # When
    model.run()

    # Then
    assert len(model.firms) == 0
    assert len(model.banks) == 0
    assert len(model.households) == 10
    assert len(model.governments) == 2
    assert len(model.national_central_banks) == 2
    assert model.union_central_bank is not None


def test_run_all_steps(params):
    # Given
    params["steps"] = 100
    params["household_number"] = 5
    params["country_number"] = 2
    model = EcoModel(params)

    # When
    model.run()

    # Then
    assert len(model.firms) > 0
