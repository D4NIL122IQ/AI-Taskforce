"""
Tests unitaires pour backendend/modeles/graphBuilder.py

Modules testés :
  - extraire_json()             : extraction JSON depuis une reponse LLM brute
  - update_results()            : fusion de dicts de resultats (reducer LangGraph)
  - build_orchestration_graph() : construction et execution du graphe
"""

import json
import pytest
from unittest.mock import MagicMock
from backend.modeles.graphBuilder import extraire_json, update_results, build_orchestration_graph


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_agent(nom, response_content):
    agent = MagicMock()
    agent.nom = nom
    resp = MagicMock()
    resp.content = response_content
    agent.executer_prompt.return_value = resp
    return agent


# ─── Tests : extraire_json ────────────────────────────────────────────────────

class TestExtraireJson:

    def test_json_brut(self):
        texte = '{"next_agent": "developpeur", "prompt": "ecris une API"}'
        result = extraire_json(texte)
        assert result["next_agent"] == "developpeur"

    def test_bloc_markdown_avec_json(self):
        texte = '```json\n{"next_agent": "testeur", "prompt": "teste"}\n```'
        result = extraire_json(texte)
        assert result["next_agent"] == "testeur"

    def test_bloc_markdown_sans_mot_json(self):
        texte = '```\n{"next_agent": "reconstructeur", "prompt": ""}\n```'
        result = extraire_json(texte)
        assert result["next_agent"] == "reconstructeur"

    def test_json_entouré_de_texte(self):
        texte = 'Voici ma decision: {"next_agent": "analyste", "prompt": "analyse"} merci.'
        result = extraire_json(texte)
        assert result["next_agent"] == "analyste"

    def test_texte_sans_json_leve_exception(self):
        with pytest.raises(json.JSONDecodeError):
            extraire_json("Pas de JSON ici du tout.")

    def test_json_malformé_leve_exception(self):
        with pytest.raises(json.JSONDecodeError):
            extraire_json('{"next_agent": "test", "prompt": }')

    def test_json_vide(self):
        result = extraire_json('{}')
        assert result == {}


# ─── Tests : update_results ───────────────────────────────────────────────────

class TestUpdateResults:

    def test_premier_resultat(self):
        result = update_results({}, {"developpeur": "code"})
        assert result == {"developpeur": "code"}

    def test_fusion_deux_resultats(self):
        existing = {"developpeur": "code"}
        result = update_results(existing, {"testeur": "tests OK"})
        assert result == {"developpeur": "code", "testeur": "tests OK"}

    def test_current_none_retourne_new(self):
        result = update_results(None, {"agent": "reponse"})
        assert result == {"agent": "reponse"}

    def test_ne_mute_pas_original(self):
        original = {"developpeur": "code"}
        update_results(original, {"testeur": "tests"})
        assert "testeur" not in original

    def test_ecrase_cle_existante(self):
        result = update_results({"agent": "old"}, {"agent": "new"})
        assert result["agent"] == "new"


# ─── Tests : build_orchestration_graph ───────────────────────────────────────

class TestBuildOrchestrationGraph:

    def test_graphe_compile_sans_erreur(self):
        sup = make_agent("superviseur", '{"next_agent": "reconstructeur", "prompt": ""}')
        sp  = make_agent("developpeur", "code")
        rec = make_agent("reconstructeur", "synthese")
        graph = build_orchestration_graph(sup, [sp], rec)
        assert graph is not None

    def test_execution_directe_vers_reconstructeur(self):
        sup = make_agent("superviseur", '{"next_agent": "reconstructeur", "prompt": ""}')
        sp  = make_agent("developpeur", "code")
        rec = make_agent("reconstructeur", "reponse finale OK")
        graph = build_orchestration_graph(sup, [sp], rec)
        state = {"user_input": "test", "results": {}, "next_agent": "", "task_for_agent": "", "final_response": ""}
        result = graph.invoke(state, config={"recursion_limit": 10})
        assert result["final_response"] == "reponse finale OK"

    def test_passage_par_specialiste(self):
        compteur = {"n": 0}
        sup = MagicMock()
        sup.nom = "superviseur"
        def side_effect(prompt):
            r = MagicMock()
            if compteur["n"] == 0:
                r.content = '{"next_agent": "developpeur", "prompt": "ecris le code"}'
            else:
                r.content = '{"next_agent": "reconstructeur", "prompt": ""}'
            compteur["n"] += 1
            return r
        sup.executer_prompt.side_effect = side_effect

        sp  = make_agent("developpeur", "voici le code")
        rec = make_agent("reconstructeur", "synthese complete")
        graph = build_orchestration_graph(sup, [sp], rec)
        state = {"user_input": "cree API", "results": {}, "next_agent": "", "task_for_agent": "", "final_response": ""}
        result = graph.invoke(state, config={"recursion_limit": 20})
        assert result["final_response"] == "synthese complete"
        sp.executer_prompt.assert_called_once_with("ecris le code")

    def test_fallbackendend_json_invalide(self):
        sup = make_agent("superviseur", "je sais pas")
        sp  = make_agent("developpeur", "code")
        rec = make_agent("reconstructeur", "reponse fallbackendend")
        graph = build_orchestration_graph(sup, [sp], rec)
        state = {"user_input": "test", "results": {}, "next_agent": "", "task_for_agent": "", "final_response": ""}
        result = graph.invoke(state, config={"recursion_limit": 10})
        assert result["final_response"] == "reponse fallbackendend"

    def test_plusieurs_specialistes(self):
        sup = make_agent("superviseur", '{"next_agent": "reconstructeur", "prompt": ""}')
        rec = make_agent("reconstructeur", "ok")
        specialistes = [make_agent(n, "rep") for n in ["dev", "testeur", "designer"]]
        graph = build_orchestration_graph(sup, specialistes, rec)
        assert graph is not None
