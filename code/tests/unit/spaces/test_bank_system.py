import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import BankSystem

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(BankSystem, EcoSpace)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def bank_system():
    # Given
    model = Mock()
    space = BankSystem(model)
    return space


class FakeRole:
    pass


def test_add_commercial_bank_creates_commercial_bank_role(bank_system, monkeypatch):
    # Given
    agent = Mock()
    bank_system.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.CommercialBankRole", FakeRole)

    # When
    commercial_bank = bank_system.add_commercial_bank(agent)

    # Then
    action = bank_system.add_role
    action.assert_called_with(FakeRole, agent, "commercial_bank")
    assert commercial_bank is action.return_value


def test_add_central_bank_creates_central_bank_role(bank_system, monkeypatch):
    # Given
    agent = Mock()
    bank_system.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.CentralBankRole", FakeRole)

    # When
    central_bank = bank_system.add_central_bank(agent)

    # Then
    action = bank_system.add_role
    action.assert_called_with(FakeRole, agent, "central_bank")
    assert central_bank is action.return_value


def test_assign_central_bank_by_adding_graph_edge(bank_system):
    # Given
    bank_role = Mock()
    central_role = Mock()
    graph = bank_system.graph
    graph.add_nodes_from([bank_role, central_role])

    # When
    bank_system.assign_central_bank(bank_role, central_role)

    # Then
    edges = list(graph.edges)
    source, target = edges[0]
    assert len(edges) == 1
    assert source is central_role
    assert target is bank_role
    assert bank_role.central_bank is central_role
