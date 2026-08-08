import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import CentralBankSpace

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(CentralBankSpace, EcoSpace)


@pytest.fixture
def central_space():
    # Given
    model = Mock()
    space = CentralBankSpace(model)
    return space


def test_has_default_discount_rate(central_space):
    # Assert
    assert central_space.discount_rate == 0


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


class FakeRole:
    pass


def test_add_commercial_bank_creates_commercial_bank_role(central_space, monkeypatch):
    # Given
    agent = Mock()
    central_space.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.CommercialBankRole", FakeRole)

    # When
    commercial_bank = central_space.add_commercial_bank(agent)

    # Then
    action = central_space.add_role
    action.assert_called_with(FakeRole, agent, "commercial_bank")
    assert commercial_bank is action.return_value


def test_add_central_bank_creates_central_bank_role(central_space, monkeypatch):
    # Given
    agent = Mock()
    central_space.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.CentralBankRole", FakeRole)

    # When
    central_bank = central_space.add_central_bank(agent)

    # Then
    action = central_space.add_role
    action.assert_called_with(FakeRole, agent, "central_bank")
    assert central_bank is action.return_value


# def test_pay_deposit_interest():

#     bank = BankAgent()
#     bank.deposit_rate = 0.04

#     holder_agent = Mock()
#     holder_agent.deposits = 1000

#     holder_role = Mock()
#     holder_role.agent = holder_agent

#     bank_role = DepositBankRole(bank)

#     bank_role.pay_deposit_interest(holder_role)

#     holder_agent.increase_stocks.assert_called_once_with("deposits", 40)

#     holder_agent.increase_flows.assert_called_once_with("deposit_interest", 40)

#     bank.decrease_stocks.assert_called_once_with("deposits", 40)

#     bank.increase_flows.assert_called_once_with("deposit_interest_paid", 40)
