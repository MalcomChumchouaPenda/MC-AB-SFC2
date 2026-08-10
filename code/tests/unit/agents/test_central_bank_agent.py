import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import CentralBankAgent

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from mc_ab_sfc.base import EcoAgent

    # Assert
    assert issubclass(CentralBankAgent, EcoAgent)


@pytest.fixture
def central_bank():
    # Given
    model = Mock()
    return CentralBankAgent(model)


def test_has_default_discount_rate(central_bank):
    # Assert
    assert central_bank.discount_rate == 0


def test_has_default_stocks(central_bank):
    # Assert
    assert central_bank.bonds == 0
    assert central_bank.reserves == 0
    assert central_bank.cash_advances == 0


# ---------------------------------------------------
# BEHAVIORS TESTS
# ----------------------------------------------------


def test_update_discount_rate(central_bank):
    # Given
    central_role = Mock()
    central_role.get_average_inflation.return_value = 0.04
    central_bank.roles["central_bank"] = central_role
    central_bank.discount_rate = 0.03
    central_bank.p.long_run_rate = 0.02
    central_bank.p.xi = 0.5
    central_bank.p.xi_deltap = 1.5
    central_bank.p.inflation_target = 0.02

    # When
    central_bank.update_discount_rate()

    # Then
    assert central_bank.discount_rate == pytest.approx(0.04)


@pytest.fixture
def bond_issuers():
    # Given
    return [
        Mock(bond_supply=100),
        Mock(bond_supply=100),
    ]


@pytest.fixture
def bond_buyer(bond_issuers):
    # Given
    buyer_role = Mock()
    buyer_role.get_bond_issuers.return_value = bond_issuers
    return buyer_role


def test_buy_all_remaining_bonds(bond_buyer, bond_issuers):
    # Given
    central_bank = CentralBankAgent(model=Mock())
    central_bank.roles["bond_buyer"] = bond_buyer
    bond_buyer = central_bank.roles["bond_buyer"]

    # When
    central_bank.buy_remaining_bonds()

    # Then
    for bond_issuer in bond_issuers:
        bond_buyer.buy_bonds.assert_any_call(bond_issuer, 100)


def test_calc_profit():
    # Given
    central_bank = CentralBankAgent(model=Mock())
    central_bank.bond_interest = 100
    central_bank.cash_advance_interest = 40
    central_bank.reserve_interest = 20

    # When
    profit = central_bank.calc_profit()

    # Then
    assert profit == 120


# def test_pays_profits_to_government():
#     # Given

#     central_bank = CentralBankAgent(model=Mock())

#     central_bank = CentralBankAgent()
#     government = GovernmentAgent()
#     central_bank.net_cash_flow = 120

#     central_bank.pay_profits(government)

#     assert government.cash == 120

#     assert central_bank.net_cash_flow == 0
