import pytest
from model.base import EcoAccount

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherit_from_agentpy_attrdict():
    # Given
    from agentpy import AttrDict

    # When
    is_derived = issubclass(EcoAccount, AttrDict)

    # Then
    assert is_derived


def test_creates_default_value_for_financial_assets(monkeypatch):
    # Given
    monkeypatch.setattr("model.base.FINANCIAL_ASSETS", ["x", "y"])
    monkeypatch.setattr("model.base.REAL_ASSETS", [])
    monkeypatch.setattr("model.base.TRANSACTIONS", [])

    # When
    account = EcoAccount()

    # Then
    assert account == {"x": 0.0, "y": 0.0}


def test_creates_default_value_for_real_assets(monkeypatch):
    # Given
    monkeypatch.setattr("model.base.FINANCIAL_ASSETS", [])
    monkeypatch.setattr("model.base.REAL_ASSETS", ["z"])
    monkeypatch.setattr("model.base.TRANSACTIONS", [])

    # When
    account = EcoAccount()

    # Then
    assert account == {"z": 0.0}


def test_creates_default_value_for_transactions(monkeypatch):
    # Given
    monkeypatch.setattr("model.base.FINANCIAL_ASSETS", [])
    monkeypatch.setattr("model.base.REAL_ASSETS", [])
    monkeypatch.setattr("model.base.TRANSACTIONS", ["a", "b"])

    # When
    account = EcoAccount()

    # Then
    assert account == {"a": 0.0, "b": 0.0}


# ---------------------------------------------------
# STOCKS ACCOUNTING
# ----------------------------------------------------


def test_clear_flows_reset_amount(monkeypatch):
    # Given
    monkeypatch.setattr("model.base.FINANCIAL_ASSETS", [])
    monkeypatch.setattr("model.base.REAL_ASSETS", [])
    monkeypatch.setattr("model.base.TRANSACTIONS", ["a"])
    account = EcoAccount()
    account["a"] = 500

    # When
    account.clear_flows()

    # Then
    assert account["a"] == 0
