import pytest
from agentpy.objects import Object
from model.base import EcoStock


def test_is_agentpy_object():
    # Assert
    assert issubclass(EcoStock, Object)



