import os
import sys
import pytest
from unittest.mock import Mock
from agentpy import AgentDList

root_dir = os.path.abspath(__file__)
while "tests" in root_dir:
    root_dir = os.path.dirname(root_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)


@pytest.fixture
def fake_model():
    model = Mock(t=0)
    model.random = Mock()
    return model


@pytest.fixture
def make_dlist():
    def f(content=[]):
        model = Mock()
        return AgentDList(model, content)

    return f
