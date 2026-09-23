import pytest
from unittest.mock import Mock
from agentpy import AttrDict
from model.base import EcoAccount

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_agentpy_attr_dict():
    # Assert
    assert issubclass(EcoAccount, AttrDict)


def test_has_stock_names_constant():
    # Assert
    assert EcoAccount.STOCK_NAMES == (
        "deposits",
        "loans",
        "inventories",
        "bonds",
        "cash",
        "advances",
        "equities",
    )


def test_has_flow_names_constant():
    # Assert
    assert EcoAccount.FLOW_NAMES == (
        "consumption",
        "wages",
        "public_transfers",
        "taxes",
        "dep_interests",
        "loan_interests",
        "loan_defaults",
        "bond_interests",
        "cash_interests",
        "adv_interests",
        "dividends",
        "profit_transfers",
    )


def test_contains_initial_value_for_each_stock(monkeypatch):
    # Given
    monkeypatch.setattr(EcoAccount, "STOCK_NAMES", ["x", "y"])
    monkeypatch.setattr(EcoAccount, "FLOW_NAMES", [])

    # When
    account = EcoAccount()

    # Then
    assert account == {"x": 0, "y": 0}


def test_contains_initial_value_for_each_flow(monkeypatch):
    # Given
    monkeypatch.setattr(EcoAccount, "STOCK_NAMES", [])
    monkeypatch.setattr(EcoAccount, "FLOW_NAMES", ["a", "b"])

    # When
    account = EcoAccount()

    # Then
    assert account == {"a": 0, "b": 0}


# ---------------------------------------------------
# ACCOUNTING TESTS
# ----------------------------------------------------


def test_debit_decrease_amount():
    # Given
    account = EcoAccount()

    # When
    account.debit("cash", 100)

    # Then
    assert account["cash"] == -100


def test_credit_increase_amount():
    # Given
    account = EcoAccount()

    # When
    account.credit("cash", 100)

    # Then
    assert account["cash"] == 100


def test_clear_flows_reset_amount():
    # Given
    account = EcoAccount()
    account["consumption"] = 500

    # When
    account.clear_flows()

    # Then
    assert account["consumption"] == 0
