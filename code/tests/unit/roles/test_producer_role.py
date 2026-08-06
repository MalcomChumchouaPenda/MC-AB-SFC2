import pytest
from unittest.mock import Mock
from mcabsfc.roles import ProducerRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mcabsfc.base import EcoRole

    # Assert
    assert issubclass(ProducerRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def producer():
    # Given
    market = Mock()
    owner = Mock(id=1)
    return ProducerRole(owner, market)


def test_get_location(producer):
    # Given
    firm = producer.owner
    firm.location = 0.9

    # When
    location = producer.get_location()

    # Then
    assert location == 0.9


def test_get_price(producer):
    # Given
    firm = producer.owner
    firm.price = 15

    # When
    price = producer.get_price()

    # Then
    assert price == 15


def test_get_available_quantity(producer):
    # Given
    firm = producer.owner
    firm.inventories = 100

    # When
    quantity = producer.get_available_quantity()

    # Then
    assert quantity == 100
