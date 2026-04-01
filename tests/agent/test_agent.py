import pytest
from backend.modeles.Agent import Agent


"""
Tests unitaires de la classe Agent.

Ces tests vérifient :
- la bonne initialisation d’un agent
- la validation des paramètres
- le comportement des setters
- l’exécution des prompts
- l’ajout de documents
"""


#  Test création agent
def test_agent_creation():
    """
    Vérifie que l'agent est correctement initialisé
    avec des paramètres valides.
    """
    agent = Agent("test", "Gemini", "assistant", 512, 0.5)

    assert agent.nom == "test"
    assert agent.modele == "Gemini"
    assert agent.temperature == 0.5


# Test validation nom
def test_invalid_name():
    """
    Vérifie qu'une erreur est levée si le nom est invalide (vide).
    """
    with pytest.raises(ValueError):
        Agent("", "Ollama", "assistant", 512, 0.5)


#  Test validation modèle
def test_invalid_model():
    """
    Vérifie qu'une erreur est levée si le modèle n'est pas supporté.
    """
    with pytest.raises(ValueError):
        Agent("test", "Unknown", "assistant", 512, 0.5)


#  Test la validation du prompt vide
def test_invalid_prompt():
    """
    Vérifie qu'une erreur est levée si le prompt est vide.
    """
    with pytest.raises(ValueError):
        Agent("test", "Mistral", "", 512, 0.5)


#  Test max_token invalide
def test_invalid_max_token():
    """
    Vérifie qu'une erreur est levée si max_token est invalide.
    """
    with pytest.raises(ValueError):
        Agent("test", "Mistral", "assistant", -1, 0.5)


# Test température invalide
def test_invalid_temperature():
    """
    Vérifie qu'une erreur est levée si la température est hors intervalle [0,1].
    """
    with pytest.raises(ValueError):
        Agent("test", "Mistral", "assistant", 512, 2)


# Test setter modèle
def test_set_modele():
    """
    Vérifie que le setter du modèle met bien à jour la valeur.
    """
    agent = Agent("test", "Mistral", "assistant", 512, 0.5)
    agent.modele = "Mistral"

    assert agent.modele == "Mistral"


# Test setter température
def test_set_temperature():
    """
    Vérifie que le setter de la température fonctionne correctement.
    """
    agent = Agent("test", "Ollama", "assistant", 512, 0.5)
    agent.temperature = 0.7

    assert agent.temperature == 0.7


# Tests du max_tokens
def test_set_max_token():
    """
    Vérifie que le setter de max_token met bien à jour la valeur.
    """
    agent = Agent("test", "Mistral", "assistant", 512, 0.5)
    agent.max_token = 256

    assert agent.max_token == 256


def test_empty_prompt_execution():
    """
    Vérifie qu'une erreur est levée si on exécute un prompt vide.
    """
    agent = Agent("test", "Mistral", "assistant", 512, 0.5)

    with pytest.raises(ValueError):
        agent.executer_prompt("")


# test de l'enrichissement du prompt par le fichier
def test_ajouter_document_txt(tmp_path):
    """
    Vérifie que le contenu d’un fichier texte est bien ajouté au prompt.
    """
    file = tmp_path / "test.txt"
    file.write_text("contenu test")

    agent = Agent("test", "Mistral", "assistant", 512, 0.5)
    agent.ajouter_document(str(file))

    assert "contenu test" in agent.prompt


#test du retour de l'execution d'un agent
def test_agent_response():
    """
    Vérifie que l’agent retourne une réponse cohérente
    pour une requête simple (ex: calcul).
    """
    agent= Agent("test", "Mistral", "calculatrice", 112, 0.1)
    response = agent.executer_prompt("combien font 12 multiplié par 3")

    assert "36" in response.content