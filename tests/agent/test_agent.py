import pytest
from back.logic.Agent import Agent


#  Test création agent
def test_agent_creation():
    agent = Agent("test", "Ollama", "assistant", 512, 0.5)

    assert agent.nom == "test"
    assert agent.modele == "Ollama"
    assert agent.temperature == 0.5


# Test validation nom
def test_invalid_name():
    with pytest.raises(ValueError):
        Agent("", "Ollama", "assistant", 512, 0.5)


#  Test validation modèle
def test_invalid_model():
    with pytest.raises(ValueError):
        Agent("test", "Unknown", "assistant", 512, 0.5)


#  Test la validation du prompt vide
def test_invalid_prompt():
    with pytest.raises(ValueError):
        Agent("test", "Ollama", "", 512, 0.5)


#  Test max_token invalide
def test_invalid_max_token():
    with pytest.raises(ValueError):
        Agent("test", "Ollama", "assistant", -1, 0.5)


# Test température invalide
def test_invalid_temperature():
    with pytest.raises(ValueError):
        Agent("test", "Ollama", "assistant", 512, 2)


# Test setter modèle
def test_set_modele():
    agent = Agent("test", "Ollama", "assistant", 512, 0.5)
    agent.modele = "Mistral"

    assert agent.modele == "Mistral"


# Test setter température
def test_set_temperature():
    agent = Agent("test", "Ollama", "assistant", 512, 0.5)
    agent.temperature = 0.7

    assert agent.temperature == 0.7


# Tests du max_tokens
def test_set_max_token():
    agent = Agent("test", "Ollama", "assistant", 512, 0.5)
    agent.max_token = 256

    assert agent.max_token == 256

def test_empty_prompt_execution():
    agent = Agent("test", "Ollama", "assistant", 512, 0.5)

    with pytest.raises(ValueError):
        agent.executer_prompt("")

# test de l'enrichissement du prompt par le fichier
def test_ajouter_document_txt(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("contenu test")

    agent = Agent("test", "Ollama", "assistant", 512, 0.5)
    agent.ajouter_document(str(file))

    assert "contenu test" in agent.prompt

#test du retour de l'execution d'un agent
def test_agent_response():
    agent= Agent("test", "Ollama", "calculatrice", 112, 0.1)
    response = agent.executer_prompt("combien font 12 multiplié par 3")

    assert "36" in response.content