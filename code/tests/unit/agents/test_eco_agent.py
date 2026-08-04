
import pytest
import agentpy as ap
from mcabsfc.agents import EcoAgent


# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_agent():
    # Given 
    model = ap.Model()

    # When
    agent = EcoAgent(model)

    # Then
    assert isinstance(agent, ap.Agent)
    


def test_has_roles_dict():
    # Given
    model = ap.Model()

    # When
    agent = EcoAgent(model)

    # Then
    assert agent.roles == {}


def test_has_stocks_dict():
    # Given
    model = ap.Model()

    # When
    agent = EcoAgent(model)

    # Then
    assert agent.stocks == {}
    

def test_has_flows_dict():
    # Given
    model = ap.Model()

    # When
    agent = EcoAgent(model)

    # Then
    assert agent.flows == {}


