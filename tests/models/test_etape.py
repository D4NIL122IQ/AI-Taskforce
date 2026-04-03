import pytest
from sqlalchemy.exc import IntegrityError
from backend.models.etape_model import Etape, TRANSITIONS_VALIDES, STATUTS_VALIDES


class TestEtapeCreation:
    """Tests de création et persistance."""

    def test_creation_valide(self, session, agent_actif, workflow_simple):
        etape = Etape(
            ordre_execution=1,
            description_tache="Analyser les données",
            statut_etape="EN_ATTENTE",
            agent_id=agent_actif.id_agent,
            workflow_id=workflow_simple.id_workflow,
        )
        session.add(etape)
        session.commit()

        result = session.query(Etape).filter_by(ordre_execution=1).first()
        assert result is not None
        assert result.description_tache == "Analyser les données"

    def test_valeur_defaut_statut(self, session, workflow_simple):
        etape = Etape(ordre_execution=1, workflow_id=workflow_simple.id_workflow)
        session.add(etape)
        session.commit()
        assert etape.statut_etape == "EN_ATTENTE"

    def test_agent_optionnel(self, session, workflow_simple):
        """Une étape peut exister sans agent assigné."""
        etape = Etape(ordre_execution=1, workflow_id=workflow_simple.id_workflow)
        session.add(etape)
        session.commit()
        assert etape.agent_id is None

    def test_workflow_obligatoire(self, session):
        etape = Etape(ordre_execution=1)
        session.add(etape)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_ordre_execution_obligatoire(self, session, workflow_simple):
        etape = Etape(workflow_id=workflow_simple.id_workflow)
        session.add(etape)
        with pytest.raises(IntegrityError):
            session.commit()


class TestEtapeOrdre:
    """Vérifie la contrainte ordre_execution >= 1."""

    @pytest.mark.parametrize("ordre", [1, 5, 100])
    def test_ordre_valide(self, session, workflow_simple, ordre):
        etape = Etape(ordre_execution=ordre, workflow_id=workflow_simple.id_workflow)
        session.add(etape)
        session.commit()
        assert etape.id_etape is not None

    @pytest.mark.parametrize("ordre", [0, -1, -10])
    def test_ordre_invalide(self, session, workflow_simple, ordre):
        etape = Etape(ordre_execution=ordre, workflow_id=workflow_simple.id_workflow)
        session.add(etape)
        with pytest.raises(IntegrityError):
            session.commit()


class TestEtapeStatuts:
    """Vérifie les contraintes sur statut_etape."""

    @pytest.mark.parametrize("statut", ["EN_ATTENTE", "EN_COURS", "TERMINE", "ERREUR"])
    def test_statut_valide(self, session, workflow_simple, statut):
        etape = Etape(ordre_execution=1, statut_etape=statut,
                      workflow_id=workflow_simple.id_workflow)
        session.add(etape)
        session.commit()
        assert etape.statut_etape == statut

    def test_statut_invalide(self, session, workflow_simple):
        etape = Etape(ordre_execution=1, statut_etape="INCONNU",
                      workflow_id=workflow_simple.id_workflow)
        session.add(etape)
        with pytest.raises(IntegrityError):
            session.commit()


class TestEtapeTransitions:
    """Vérifie la machine à états (TRANSITIONS_VALIDES)."""

    def test_transitions_depuis_en_attente(self):
        assert TRANSITIONS_VALIDES["EN_ATTENTE"] == ["EN_COURS"]

    def test_transitions_depuis_en_cours(self):
        assert set(TRANSITIONS_VALIDES["EN_COURS"]) == {"TERMINE", "ERREUR"}

    def test_termine_est_terminal(self):
        assert TRANSITIONS_VALIDES["TERMINE"] == []

    def test_erreur_permet_retry(self):
        assert TRANSITIONS_VALIDES["ERREUR"] == ["EN_ATTENTE"]

    def test_tous_les_statuts_couverts(self):
        assert set(TRANSITIONS_VALIDES.keys()) == STATUTS_VALIDES


class TestEtapeRelations:
    """Vérifie les relations."""

    def test_relation_workflow(self, session, workflow_simple):
        etape = Etape(ordre_execution=1, workflow_id=workflow_simple.id_workflow)
        session.add(etape)
        session.commit()
        assert etape.workflow.nom == workflow_simple.nom

    def test_relation_agent(self, session, agent_actif, workflow_simple):
        etape = Etape(ordre_execution=1, agent_id=agent_actif.id_agent,
                      workflow_id=workflow_simple.id_workflow)
        session.add(etape)
        session.commit()
        assert etape.agent.nom == agent_actif.nom

    def test_plusieurs_etapes_par_workflow(self, session, workflow_simple):
        for i in range(1, 4):
            session.add(Etape(ordre_execution=i, workflow_id=workflow_simple.id_workflow))
        session.commit()
        assert len(workflow_simple.etapes) == 3
