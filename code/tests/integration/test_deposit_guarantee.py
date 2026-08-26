import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import FirmAgent, BankAgent, CentralBankAgent, GovernmentAgent
from mc_ab_sfc.spaces import BondMarket, DepositMarket, CountrySpace


@pytest.fixture
def model():
    return Mock()


@pytest.fixture
def country(model):
    # Given
    return CountrySpace(model)


@pytest.fixture
def bond_market(model):
    # Given
    bond_market = BondMarket(model)
    bond_market.setup()
    return bond_market


@pytest.fixture
def cb(model, bond_market):
    # Given
    cb = CentralBankAgent(model)
    bond_market.add_buyer(cb)
    return cb


@pytest.fixture
def deposit_market(model):
    # Given
    return DepositMarket(model)


@pytest.fixture
def govt(model, bond_market, deposit_market):
    # Given
    govt = GovernmentAgent(model)
    bond_market.add_issuer(govt)
    deposit_market.add_deposit_guarantee(govt)
    return govt


@pytest.fixture
def banks(model, deposit_market):
    banks = []
    for _ in range(2):
        bank = BankAgent(model)
        bank.defaulted = True
        bank.deposits = 500
        banks.append(bank)
        deposit_market.add_deposit_bank(bank)
    return banks


@pytest.fixture
def firms(model, deposit_market, banks):
    firms = []
    bank_roles = [b.roles["deposit_bank"] for b in banks]
    for i in range(10):
        firm = FirmAgent(model)
        firm.deposits = 100
        firms.append(firm)
        bank_role = bank_roles[i % 2]
        holder_role = deposit_market.add_deposit_holder(firm)
        deposit_market.assign_deposit_bank(holder_role, bank_role)
    return firms


def test_government_activate_deposit_guarantee(govt, firms, banks):
    # When
    govt.issue_deposit_guarantee_bonds()
    govt.reimburse_deposits()

    # Then
    assert govt.bond_supply == 1000
    assert govt.reserves == -1000
    for firm in firms:
        assert firm.deposits == 0
        assert firm.cash == 100
    for bank in banks:
        assert bank.deposits == 0
        assert bank.reserves == 0
