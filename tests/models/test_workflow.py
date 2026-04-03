import pytest
from sqlalchemy.exc import IntegrityError
from backend.models.workflow_model import Workflow
from backend.models.agent_model import Agent
from backend.models.etape_model import Etape
from backend.models.execution_model import Execution


class TestWorkflowCreation:
    """Tests de création et persistance."""

    def test_creation_minimale(self, session):
        wf = Workflow(nom="Workflow Simple")
        session.add(wf)
        session.commit()

        result = session.query(Workflow).filter_by(nom="Workflow Simple").first()
        assert result is not None
        assert result.superviseur_id is None

    def test_creation_avec_superviseur(self, session, agent_actif):
        wf = Workflow(nom="Workflow Supervisé", superviseur_id=agent_actif.id_agent)
        session.add(wf)
        session.commit()
        assert wf.superviseur.nom == agent_actif.nom

    def test_date_creation_auto(self, session):
        wf = Workflow(nom="Workflow Date")
        session.add(wf)
        session.commit()
        assert wf.date_creation is not None

    def test_nom_obligatoire(self, session):
        wf = Workflow()
        session.add(wf)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_donnees_graphe_optionnel(self, session):
        wf = Workflow(nom="Sans Graphe")
        session.add(wf)
        session.commit()
        assert wf.donnees_graphe_json is None

    def test_donnees_graphe_json(self, session):
        graphe = {"nodes": [{"id": 1}], "edges": []}
        wf = Workflow(nom="Avec Graphe", donnees_graphe_json=graphe)
        session.add(wf)
        session.commit()
        assert wf.donnees_graphe_json == graphe


class TestWorkflowRelations:
    """Vérifie les relations de Workflow."""

    def test_relation_superviseur(self, session, agent_actif):
        wf = Workflow(nom="Supervisé", superviseur_id=agent_actif.id_agent)
        session.add(wf)
        session.commit()
        assert wf.superviseur is not None
        assert wf.superviseur.id_agent == agent_actif.id_agent

    def test_superviseur_optionnel(self, session):
        wf = Workflow(nom="Sans Superviseur")
        session.add(wf)
        session.commit()
        assert wf.superviseur is None

    def test_superviseur_inexistant(self, session):
        wf = Workflow(nom="Superviseur Fantôme", superviseur_id=9999)
        session.add(wf)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_cascade_etapes(self, session, workflow_simple):
        for i in range(1, 3):
            session.add(Etape(ordre_execution=i, workflow_id=workflow_simple.id_workflow))
        session.commit()

        session.delete(workflow_simple)
        session.commit()

        assert session.query(Etape).count() == 0

    def test_cascade_executions(self, session, workflow_simple):
        exec_ = Execution(workflow_id=workflow_simple.id_workflow)
        session.add(exec_)
        session.commit()

        session.delete(workflow_simple)
        session.commit()

        assert session.query(Execution).count() == 0

    def test_plusieurs_etapes(self, session, workflow_simple):
        for i in range(1, 5):
            session.add(Etape(ordre_execution=i, workflow_id=workflow_simple.id_workflow))
        session.commit()
        assert len(workflow_simple.etapes) == 4

    def test_plusieurs_executions(self, session, workflow_simple):
        for _ in range(3):
            session.add(Execution(workflow_id=workflow_simple.id_workflow))
        session.commit()
        assert len(workflow_simple.executions) == 3


class TestWorkflowIntegration:
    """Tests de scénarios complets."""

    def test_workflow_complet(self, session):
        """Crée un workflow avec agent superviseur, étapes et une exécution."""
        agent = Agent(nom="Superviseur", modele="Anthropic")
        session.add(agent)
        session.flush()

        wf = Workflow(nom="Workflow Complet", superviseur_id=agent.id_agent)
        session.add(wf)
        session.flush()

        for i in range(1, 4):
            session.add(Etape(
                ordre_execution=i,
                description_tache=f"Étape {i}",
                workflow_id=wf.id_workflow,
                agent_id=agent.id_agent,
            ))

        exec_ = Execution(workflow_id=wf.id_workflow, status="EN_COURS")
        session.add(exec_)
        session.commit()

        assert len(wf.etapes) == 3
        assert len(wf.executions) == 1
        assert wf.superviseur.nom == "Superviseur"

    def test_suppression_agent_superviseur_ne_supprime_pas_workflow(self, session, agent_actif, workflow_simple):
        """La suppression de l'agent superviseur ne doit pas supprimer le workflow."""
        # Le superviseur_id devient NULL si on supprime l'agent
        # (dépend de la config ondelete, ici on vérifie que le workflow existe encore)
        wf_id = workflow_simple.id_workflow
        session.delete(agent_actif)
        session.commit()

        wf = session.query(Workflow).get(wf_id)
        assert wf is not None
