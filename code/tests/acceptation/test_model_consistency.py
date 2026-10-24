import pytest
from model.model import EcoModel
from model.accounts import FINANCIAL_ASSETS, TRANSACTIONS


@pytest.fixture(scope="session")
def params():
    # Given
    return {
        "country_number": 2,
        "household_number": 10,
        "psi": 10,
        "upsilon": 1.0,
        "omega": 0.1,
        "initial_wage": 1.0,
        "initial_phi": 1.0,
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
        "initial_public_transfer": 0.4,
        "dmax": 0.03,
        "tax_min": 0.35,
        "tax_max": 0.45,
        "g_min": 0.4,
        "g_max": 0.6,
        "eta": 0.03,
        "initial_equity": 10.0,
        "sigma": 4,
    }


@pytest.fixture(scope="session")
def result(params):
    # Given
    params["steps"] = 20
    model = EcoModel(params)
    model.run(seed=1)
    return model.output.arrange_variables()


def test_stock_consistency(result):
    # Given
    stock_names = list(FINANCIAL_ASSETS)
    stock_data = result[stock_names + ["t"]]

    # When
    total = stock_data.groupby("t").sum().copy()

    # Then
    # print(total.tail())
    for period in total.index:
        for name in total.columns:
            sub_total = round(total.loc[period, name], 6)
            print(period, name, sub_total)
            assert sub_total == pytest.approx(0)
