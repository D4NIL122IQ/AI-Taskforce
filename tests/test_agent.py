import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import pytest
from unittest.mock import MagicMock
from back.models.agent import Agent


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def agent_valide():
    return Agent(
        nom="AgentTest",
        modele="Mistral",
        temperature=0.7,
        max_tokens=1024,
        role="Tu es un assistant utile",
        system_prompt="Réponds en français"
    )


# ──────────────────────────────────────────────
# Création
# ──────────────────────────────────────────────

class TestAgentCreation:

    def test_attributs_de_base(self, agent_valide):
        assert agent_valide.nom == "AgentTest"
        assert agent_valide.modele == "Mistral"
        assert agent_valide.temperature == 0.7
        assert agent_valide.max_tokens == 1024
        assert agent_valide.statut == "ACTIF"

    def test_execution_id_absent(self, agent_valide):
        assert agent_valide.id_agent is None  # pas encore persisté

    def test_date_creation_none_avant_persistance(self, agent_valide):
        # date_creation est un default SQLAlchemy, None avant flush
        assert agent_valide.date_creation is None

    @pytest.mark.parametrize("modele", ["Openai", "Ollama", "Mistral"])
    def test_modeles_valides(self, modele):
        agent = Agent(nom="Test", modele=modele, temperature=0.5, max_tokens=512)
        assert agent.modele == modele

    @pytest.mark.parametrize("temperature", [0.0, 0.5, 1.0])
    def test_temperatures_limites(self, temperature):
        agent = Agent(nom="Test", modele="Ollama", temperature=temperature, max_tokens=512)
        assert agent.temperature == temperature

    @pytest.mark.parametrize("max_tokens", [1, 1024, 8192])
    def test_max_tokens_limites(self, max_tokens):
        agent = Agent(nom="Test", modele="Ollama", temperature=0.5, max_tokens=max_tokens)
        assert agent.max_tokens == max_tokens


# ──────────────────────────────────────────────
# modifierParametre
# ──────────────────────────────────────────────

class TestModifierParametre:

    @pytest.mark.parametrize("champ,valeur", [
        ("nom",           "NouveauNom"),
        ("role",          "Nouveau rôle"),
        ("modele",        "Openai"),
        ("temperature",   0.3),
        ("max_tokens",    2048),
        ("system_prompt", "Nouveau prompt"),
    ])
    def test_modification_champs_autorises(self, agent_valide, champ, valeur):
        agent_valide.modifierParametre(champ, valeur)
        assert getattr(agent_valide, champ) == valeur

    def test_champ_inconnu_leve_erreur(self, agent_valide):
        with pytest.raises(ValueError, match="Champ inconnu"):
            agent_valide.modifierParametre("statut", "INTERROMPU")

    def test_champ_vide_leve_erreur(self, agent_valide):
        with pytest.raises(ValueError, match="Champ inconnu"):
            agent_valide.modifierParametre("", "valeur")


# ──────────────────────────────────────────────
# killProcess
# ──────────────────────────────────────────────

class TestKillProcess:

    def test_statut_passe_a_interrompu(self, agent_valide):
        agent_valide.killProcess()
        assert agent_valide.statut == "INTERROMPU"

    def test_kill_sans_task(self, agent_valide):
        # Ne doit pas lever d'erreur si _execution_task absent
        agent_valide.killProcess()

    def test_kill_avec_task_mock(self, agent_valide):
        mock_task = MagicMock()
        agent_valide._execution_task = mock_task
        agent_valide.killProcess()
        mock_task.cancel.assert_called_once()
        assert agent_valide._execution_task is None
        assert agent_valide.statut == "INTERROMPU"

    def test_kill_deux_fois(self, agent_valide):
        agent_valide.killProcess()
        agent_valide.killProcess()  # ne doit pas lever d'erreur
        assert agent_valide.statut == "INTERROMPU"


# ──────────────────────────────────────────────
# ajouterDocument (documents commenté → comportement attendu)
# ──────────────────────────────────────────────

class TestAjouterDocument:

    def test_ajouter_document_sans_relation_leve_erreur(self, agent_valide):
        # documents est commenté → AttributeError attendu
        doc = MagicMock()
        with pytest.raises(AttributeError):
            agent_valide.ajouterDocument(doc)


# ──────────────────────────────────────────────
# __repr__
# ──────────────────────────────────────────────

class TestAgentRepr:

    def test_repr_format(self, agent_valide):
        r = repr(agent_valide)
        assert "AgentTest" in r
        assert "Mistral" in r