import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import back.models.agent
import back.models.message

import back.models.document
import back.models.etape
import back.models.execution

import pytest
from datetime import datetime
from back.models.workflow import Workflow


@pytest.fixture
def workflow_valide():
    return Workflow(
        nom="WorkflowTest",
        donnees_graphe_json={
            "superviseur": {"id": "supervisor", "modele": "gpt-4o"},
            "agents_specialises": [
                {"id": "dev",    "nom": "Développeur", "modele": "gpt-4o"},
                {"id": "tester", "nom": "Testeur",      "modele": "mistral"},
            ]
        }
    )

@pytest.fixture
def nodes_etoile():
    return [
        {"id": "supervisor", "type": "supervisor"},
        {"id": "dev",        "type": "agent"},
        {"id": "tester",     "type": "agent"},
    ]

@pytest.fixture
def edges_etoile():
    return [
        {"source": "supervisor", "target": "dev"},
        {"source": "supervisor", "target": "tester"},
        {"source": "dev",        "target": "supervisor"},
        {"source": "tester",     "target": "supervisor"},
    ]


class TestWorkflowInit:

    def test_attributs_de_base(self, workflow_valide):
        assert workflow_valide.nom            == "WorkflowTest"
        assert isinstance(workflow_valide.date_creation, datetime)

    def test_structure_json_par_defaut(self):
        wf = Workflow(nom="W")
        assert "superviseur"        in wf.donnees_graphe_json
        assert "agents_specialises" in wf.donnees_graphe_json
        assert wf.donnees_graphe_json["agents_specialises"] == []

    def test_nom_vide_leve_erreur(self):
        with pytest.raises(ValueError, match="Nom invalide"):
            Workflow(nom="")

    def test_nom_trop_long_leve_erreur(self):
        with pytest.raises(ValueError, match="Nom invalide"):
            Workflow(nom="x" * 101)


class TestWorkflowValidateWorkflow:

    def test_structure_etoile_valide(self, workflow_valide, nodes_etoile, edges_etoile):
        assert workflow_valide.validateWorkflow(nodes_etoile, edges_etoile) is True

    def test_sans_agent_leve_erreur(self, workflow_valide):
        nodes = [{"id": "supervisor", "type": "supervisor"}]
        with pytest.raises(ValueError, match="Au moins un agent"):
            workflow_valide.validateWorkflow(nodes, [])

    def test_sans_superviseur_leve_erreur(self, workflow_valide):
        nodes = [{"id": "dev", "type": "agent"}]
        with pytest.raises(ValueError, match="Exactement un superviseur"):
            workflow_valide.validateWorkflow(nodes, [])

    def test_deux_superviseurs_leve_erreur(self, workflow_valide):
        nodes = [
            {"id": "sup1", "type": "supervisor"},
            {"id": "sup2", "type": "supervisor"},
            {"id": "dev",  "type": "agent"},
        ]
        with pytest.raises(ValueError, match="Exactement un superviseur"):
            workflow_valide.validateWorkflow(nodes, [])

    def test_arete_agent_agent_interdite(self, workflow_valide, nodes_etoile):
        edges = [{"source": "dev", "target": "tester"}]
        with pytest.raises(ValueError, match="Connexion agent.*agent interdite"):
            workflow_valide.validateWorkflow(nodes_etoile, edges)

    def test_arete_hors_etoile_interdite(self, workflow_valide, nodes_etoile):
        edges = [{"source": "xxx", "target": "yyy"}]
        with pytest.raises(ValueError, match="hors structure"):
            workflow_valide.validateWorkflow(nodes_etoile, edges)


class TestWorkflowAgentsSpecialises:

    def test_ajouter_agent(self, workflow_valide):
        avant = len(workflow_valide.donnees_graphe_json["agents_specialises"])
        workflow_valide.ajouterAgentSpecialise({"id": "debug", "modele": "gpt-4o"})
        assert len(workflow_valide.donnees_graphe_json["agents_specialises"]) == avant + 1

    def test_ajouter_agent_deja_present(self, workflow_valide):
        with pytest.raises(ValueError, match="déjà présent"):
            workflow_valide.ajouterAgentSpecialise({"id": "dev", "modele": "gpt-4o"})

    def test_retirer_agent(self, workflow_valide):
        workflow_valide.retirerAgentSpecialise("tester")
        ids = [a["id"] for a in workflow_valide.donnees_graphe_json["agents_specialises"]]
        assert "tester" not in ids

    def test_retirer_superviseur_interdit(self, workflow_valide):
        with pytest.raises(ValueError, match="superviseur"):
            workflow_valide.retirerAgentSpecialise("supervisor")

    def test_retirer_agent_absent(self, workflow_valide):
        with pytest.raises(ValueError, match="absent"):
            workflow_valide.retirerAgentSpecialise("inconnu")


class TestWorkflowSuperviseur:

    def test_handle_supervisor_designate(self, workflow_valide):
        workflow_valide.handleSupervisorDesignate({"id": "new_sup", "modele": "mistral"})
        assert workflow_valide.donnees_graphe_json["superviseur"]["id"] == "new_sup"

    def test_handle_supervisor_sans_id_leve_erreur(self, workflow_valide):
        with pytest.raises(ValueError, match="id manquant"):
            workflow_valide.handleSupervisorDesignate({"modele": "gpt-4o"})


class TestWorkflowVisualiserToDict:

    def test_visualiser_retourne_structure(self, workflow_valide):
        v = workflow_valide.visualiserWorkflow()
        assert "superviseur"        in v
        assert "agents_specialises" in v

    def test_to_dict_cles(self, workflow_valide):
        d = workflow_valide.toDict()
        assert set(d.keys()) == {
            "id_workflow", "nom", "donnees_graphe_json",
            "superviseur_id", "date_creation"
        }

    def test_repr(self, workflow_valide):
        assert "WorkflowTest" in repr(workflow_valide)