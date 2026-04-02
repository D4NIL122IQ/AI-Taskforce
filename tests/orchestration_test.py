# tests/test_orchestration.py
"""
Tests unitaires pour back/modeles/orchestration.py

Ce qu on teste :
  - __init__ : cree bien le reconstructeur + compile le graph
  - executer  : retourne la final_response de l etat LangGraph
  - afficher_graphe : sauvegarde l image ou gere l exception proprement
"""

import pytest
from unittest.mock import MagicMock, patch

# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_agent_mock(nom="superviseur", modele="gemini", temperature=0.3, max_token=1000):
    agent = MagicMock()
    agent.nom = nom
    agent.modele = modele
    agent.temperature = temperature
    agent.max_token = max_token
    return agent


# ─── Tests : __init__ ─────────────────────────────────────────────────────────

class TestOrchestrationInit:

    @patch("back.modeles.orchestration.build_orchestration_graph")
    @patch("back.modeles.orchestration.Agent")
    def test_reconstructeur_cree_avec_params_superviseur(self, MockAgent, mock_build):
        mock_build.return_value = MagicMock()
        sup = make_agent_mock(nom="superviseur", modele="gemini", temperature=0.3, max_token=2000)
        sp  = make_agent_mock(nom="developpeur")

        from back.modeles.orchestration import Orchestration
        orche = Orchestration(superviseur=sup, specialistes=[sp])

        MockAgent.assert_called_once()
        call_kwargs = MockAgent.call_args[1]
        assert call_kwargs["nom"] == "reconstructeur"
        assert call_kwargs["modele"] == "gemini"
        assert call_kwargs["max_token"] == 2000
        assert call_kwargs["temperature"] == 0.5

    @patch("back.modeles.orchestration.build_orchestration_graph")
    @patch("back.modeles.orchestration.Agent")
    def test_graph_compile_appele(self, MockAgent, mock_build):
        mock_build.return_value = MagicMock()
        sup = make_agent_mock()
        sp  = make_agent_mock(nom="sp")

        from back.modeles.orchestration import Orchestration
        Orchestration(superviseur=sup, specialistes=[sp])

        mock_build.assert_called_once()

    @patch("back.modeles.orchestration.build_orchestration_graph")
    @patch("back.modeles.orchestration.Agent")
    def test_attributs_assignes(self, MockAgent, mock_build):
        mock_build.return_value = MagicMock()
        sup = make_agent_mock(nom="superviseur")
        sp  = make_agent_mock(nom="sp")

        from back.modeles.orchestration import Orchestration
        orche = Orchestration(superviseur=sup, specialistes=[sp])

        assert orche.superviseur is sup
        assert orche.specialistes == [sp]
        assert orche.graph is mock_build.return_value


# ─── Tests : executer ─────────────────────────────────────────────────────────

class TestOrchestrationExecuter:

    def _make_orchestration(self, final_response="reponse finale"):
        with patch("back.modeles.orchestration.build_orchestration_graph") as mock_build, \
             patch("back.modeles.orchestration.Agent"):

            mock_graph = MagicMock()
            mock_graph.invoke.return_value = {
                "user_input": "prompt test",
                "results": {},
                "next_agent": "reconstructeur",
                "task_for_agent": "",
                "final_response": final_response
            }
            mock_build.return_value = mock_graph

            from back.modeles.orchestration import Orchestration
            sup = make_agent_mock()
            sp  = make_agent_mock(nom="sp")
            orche = Orchestration(superviseur=sup, specialistes=[sp])
            orche.graph = mock_graph
            return orche

    def test_retourne_final_response(self):
        orche = self._make_orchestration("ma reponse attendue")
        result = orche.executer("mon prompt")
        assert result == "ma reponse attendue"

    def test_graph_invoke_appele_avec_bon_etat_initial(self):
        orche = self._make_orchestration()
        orche.executer("mon prompt utilisateur")
        call_args = orche.graph.invoke.call_args[0][0]
        assert call_args["user_input"] == "mon prompt utilisateur"
        assert call_args["results"] == {}
        assert call_args["final_response"] == ""

    def test_recursion_limit_transmis(self):
        orche = self._make_orchestration()
        orche.executer("test")
        call_kwargs = orche.graph.invoke.call_args[1]
        assert call_kwargs["config"]["recursion_limit"] == 50

    def test_final_response_absente_retourne_message_erreur(self):
        with patch("back.modeles.orchestration.build_orchestration_graph") as mock_build, \
             patch("back.modeles.orchestration.Agent"):
            mock_graph = MagicMock()
            mock_graph.invoke.return_value = {}
            mock_build.return_value = mock_graph

            from back.modeles.orchestration import Orchestration
            orche = Orchestration(superviseur=make_agent_mock(), specialistes=[make_agent_mock(nom="sp")])
            orche.graph = mock_graph

            result = orche.executer("test")
            assert "Erreur" in result


# ─── Tests : afficher_graphe ──────────────────────────────────────────────────

class TestOrchestrationAfficherGraphe:

    def _make_orche(self):
        with patch("back.modeles.orchestration.build_orchestration_graph") as mock_build, \
             patch("back.modeles.orchestration.Agent"):
            mock_build.return_value = MagicMock()
            from back.modeles.orchestration import Orchestration
            return Orchestration(superviseur=make_agent_mock(), specialistes=[make_agent_mock(nom="sp")])

    def test_sauvegarde_image(self, tmp_path):
        orche = self._make_orche()
        fake_png = b"\x89PNG fake data"
        orche.graph.get_graph.return_value.draw_mermaid_png.return_value = fake_png

        chemin = str(tmp_path / "graph_test.png")
        orche.afficher_graphe(chemin)

        with open(chemin, "rb") as f:
            assert f.read() == fake_png

    def test_exception_geree_proprement(self, capsys):
        orche = self._make_orche()
        orche.graph.get_graph.side_effect = Exception("graphviz not installed")

        orche.afficher_graphe("graph.png")

        captured = capsys.readouterr()
        assert "Impossible" in captured.out
