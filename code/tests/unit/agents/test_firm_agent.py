import agentpy as ap
from mcabsfc.agents import FirmAgent

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_agent():
    # Given
    model = ap.Model()

    # When
    agent = FirmAgent(model)

    # Then
    assert isinstance(agent, ap.Agent)


def test_has_roles_dict():
    # Given
    model = ap.Model()

    # When
    agent = FirmAgent(model)

    # Then
    assert agent.roles == {}

