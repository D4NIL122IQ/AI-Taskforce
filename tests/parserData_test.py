# tests/test_parser_data.py
"""
Tests unitaires pour backend/modeles/parserData.py

Ce qu on teste :
  - parser()        : lit un JSON valide et retourne (superviseur, specialistes, prompt)
  - _creer_agent()  : cree bien un Agent depuis un noeud JSON
  - Cas d erreur    : superviseur absent, fichier manquant, JSON invalide
"""

import json
import pytest
from unittest.mock import patch, MagicMock


# ─── Fixture JSON de workflow valide ──────────────────────────────────────────

WORKFLOW_VALIDE = {
    "nodes": [
        {
            "id": "superviseur",
            "type": "supervisor",
            "data": {
                "model": "gemini",
                "system_prompt": "Tu es superviseur.",
                "max_tokens": 2000,
                "temperature": 0.0
            }
        },
        {
            "id": "developpeur",
            "type": "agent",
            "data": {
                "model": "openai",
                "system_prompt": "Tu es developpeur.",
                "max_tokens": 1500,
                "temperature": 0.7
            }
        },
        {
            "id": "testeur",
            "type": "agent",
            "data": {
                "model": "anthropic",
                "system_prompt": "Tu es testeur.",
                "max_tokens": 1000,
                "temperature": 0.3
            }
        }
    ],
    "input": {
        "prompt": "Cree une API REST en Python"
    }
}

WORKFLOW_SANS_SUPERVISEUR = {
    "nodes": [
        {
            "id": "developpeur",
            "type": "agent",
            "data": {
                "model": "openai",
                "system_prompt": "Tu es developpeur.",
            }
        }
    ],
    "input": {"prompt": "test"}
}

WORKFLOW_SANS_PROMPT = {
    "nodes": [
        {
            "id": "superviseur",
            "type": "supervisor",
            "data": {"model": "gemini", "system_prompt": "sup"}
        }
    ]
}


# ─── Tests ────────────────────────────────────────────────────────────────────

class TestParser:

    @patch("backend.modeles.parserData.Agent")
    def test_retourne_superviseur_specialistes_prompt(self, MockAgent, tmp_path):
        filepath = tmp_path / "workflow.json"
        filepath.write_text(json.dumps(WORKFLOW_VALIDE), encoding="utf-8")

        MockAgent.side_effect = lambda **kw: MagicMock(nom=kw["nom"])

        from backend.modeles.parserData import parser
        superviseur, specialistes, prompt = parser(str(filepath))

        assert superviseur.nom == "superviseur"
        assert len(specialistes) == 2
        noms = [s.nom for s in specialistes]
        assert "developpeur" in noms
        assert "testeur" in noms

    @patch("backend.modeles.parserData.Agent")
    def test_prompt_correctement_extrait(self, MockAgent, tmp_path):
        filepath = tmp_path / "workflow.json"
        filepath.write_text(json.dumps(WORKFLOW_VALIDE), encoding="utf-8")
        MockAgent.side_effect = lambda **kw: MagicMock(nom=kw["nom"])

        from backend.modeles.parserData import parser
        _, _, prompt = parser(str(filepath))

        assert prompt == "Cree une API REST en Python"

    @patch("backend.modeles.parserData.Agent")
    def test_prompt_vide_si_absent(self, MockAgent, tmp_path):
        filepath = tmp_path / "workflow.json"
        filepath.write_text(json.dumps(WORKFLOW_SANS_PROMPT), encoding="utf-8")
        MockAgent.side_effect = lambda **kw: MagicMock(nom=kw["nom"])

        from backend.modeles.parserData import parser
        _, _, prompt = parser(str(filepath))

        assert prompt == ""

    @patch("backend.modeles.parserData.Agent")
    def test_superviseur_absent_leve_value_error(self, MockAgent, tmp_path):
        filepath = tmp_path / "workflow.json"
        filepath.write_text(json.dumps(WORKFLOW_SANS_SUPERVISEUR), encoding="utf-8")
        MockAgent.side_effect = lambda **kw: MagicMock(nom=kw["nom"])

        from backend.modeles.parserData import parser
        with pytest.raises(ValueError, match="supervisor"):
            parser(str(filepath))

    def test_fichier_inexistant_leve_erreur(self):
        from backend.modeles.parserData import parser
        with pytest.raises(FileNotFoundError):
            parser("/chemin/inexistant/workflow.json")

    @patch("backend.modeles.parserData.Agent")
    def test_agent_cree_avec_bons_parametres(self, MockAgent, tmp_path):
        filepath = tmp_path / "workflow.json"
        filepath.write_text(json.dumps(WORKFLOW_VALIDE), encoding="utf-8")
        created = []
        def capture(**kw):
            m = MagicMock(nom=kw["nom"])
            created.append(kw)
            return m
        MockAgent.side_effect = capture

        from backend.modeles.parserData import parser
        parser(str(filepath))

        # Verifier les parametres du superviseur
        sup_call = next(c for c in created if c["nom"] == "superviseur")
        assert sup_call["modele"] == "gemini"
        assert sup_call["max_token"] == 2000
        assert sup_call["temperature"] == 0.0

    @patch("backend.modeles.parserData.Agent")
    def test_valeurs_par_defaut_si_max_tokens_absent(self, MockAgent, tmp_path):
        workflow = {
            "nodes": [{
                "id": "superviseur",
                "type": "supervisor",
                "data": {"model": "gemini", "system_prompt": "sup"}
                # max_tokens et temperature absents -> valeurs par defaut
            }],
            "input": {"prompt": "test"}
        }
        filepath = tmp_path / "workflow.json"
        filepath.write_text(json.dumps(workflow), encoding="utf-8")
        created = []
        def capture(**kw):
            created.append(kw)
            return MagicMock(nom=kw["nom"])
        MockAgent.side_effect = capture

        from backend.modeles.parserData import parser
        parser(str(filepath))

        sup_call = created[0]
        assert sup_call["max_token"] == 1000   # DEFAULT_MAX_TOKENS
        assert sup_call["temperature"] == 0.3  # DEFAULT_TEMPERATURE

    @patch("backend.modeles.parserData.Agent")
    def test_aucun_specialiste_liste_vide(self, MockAgent, tmp_path):
        workflow = {
            "nodes": [{
                "id": "superviseur",
                "type": "supervisor",
                "data": {"model": "gemini", "system_prompt": "sup"}
            }],
            "input": {"prompt": "test"}
        }
        filepath = tmp_path / "workflow.json"
        filepath.write_text(json.dumps(workflow), encoding="utf-8")
        MockAgent.side_effect = lambda **kw: MagicMock(nom=kw["nom"])

        from backend.modeles.parserData import parser
        _, specialistes, _ = parser(str(filepath))

        assert specialistes == []