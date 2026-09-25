import os
import sys
import pytest
import itertools
from unittest.mock import Mock
from agentpy import AgentDList, Model

root_dir = os.path.abspath(__file__)
while "tests" in root_dir:
    root_dir = os.path.dirname(root_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)


@pytest.fixture
def fake_model():
    model = Model()
    return model


@pytest.fixture
def make_dlist(fake_model):
    def f(content=[]):
        model = fake_model
        return AgentDList(model, content)

    return f
