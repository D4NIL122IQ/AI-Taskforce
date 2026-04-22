# tests/test_agent.py

import pytest
from backend.modeles.Agent import Agent


# Test de création valide
def test_creation_agent_valide():
    agent = Agent(
        nom="TestAgent",
        modele="Openai",
        prompt="Tu es un assistant",
        max_token=100,
        temperature=0.5
    )

    assert agent.nom == "TestAgent"
    assert agent.modele == "Openai"
    assert agent.temperature == 0.5
    assert agent.max_token == 100
    assert agent.mcp is None


# Tests des validations des paramètres

def test_nom_invalide():
    with pytest.raises(ValueError):
        Agent("", "Openai", "prompt", 100, 0.5)


def test_modele_invalide():
    with pytest.raises(ValueError):
        Agent("Agent", None, "prompt", 100, 0.5)


def test_prompt_invalide():
    with pytest.raises(ValueError):
        Agent("Agent", "Openai", "", 100, 0.5)


def test_max_token_invalide():
    with pytest.raises(ValueError):
        Agent("Agent", "Openai", "prompt", -1, 0.5)


def test_temperature_invalide():
    with pytest.raises(ValueError):
        Agent("Agent", "Openai", "prompt", 100, 2)


# Test des setters

def test_modification_parametres():
    agent = Agent("A", "Openai", "prompt", 100, 0.5)

    agent.modele = "Mistral"
    agent.temperature = 0.2
    agent.max_token = 200

    assert agent.modele == "Mistral"
    assert agent.temperature == 0.2
    assert agent.max_token == 200


# Test prompt vide dans executer_prompt

def test_prompt_vide():
    agent = Agent("A", "Openai", "prompt", 100, 0.5)

    with pytest.raises(ValueError):
        agent.executer_prompt("")


# Test basique du MCP sans appel réel

def test_mcp_activation():
    agent = Agent("A", "Openai", "prompt", 100, 0.5)

    agent._mcp = "fake_connection"
    assert agent.mcp_actif is True

    agent.deconnecter_mcp()
    assert agent.mcp_actif is False