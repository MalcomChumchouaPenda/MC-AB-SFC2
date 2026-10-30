import pytest
from model.items import Cash

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_initializes_with_zero_amount():
    # Given
    cash = Cash()

    # When
    default = cash.amount

    # Then
    assert default == 0.0


def test_initializes_with_default_amount():
    # Given
    cash = Cash(amount=100)

    # When
    default = cash.amount

    # Then
    assert default == 100
