import pytest
from sqlalchemy.exc import IntegrityError
from back.models.execution_model import Execution, Resultat


class TestExecutionCreation:
    """Tests de crÃ©ation et persistance."""

    def test_creation_valide(self, session, workflow_simple):
        exec_ = Execution(workflow_id=workflow_simple.id_workflow)
        session.add(exec_)
        session.commit()

        result = session.query(Execution).get(exec_.id_execution)
        assert result is not None
        assert result.status == "EN_COURS"

    def test_valeur_defaut_status(self, session, workflow_simple):
        exec_ = Execution(workflow_id=workflow_simple.id_workflow)
        session.add(exec_)
        session.commit()
        assert exec_.status == "EN_COURS"

    def test_date_execution_auto(self, session, workflow_simple):
        exec_ = Execution(workflow_id=workflow_simple.id_workflow)
        session.add(exec_)
        session.commit()
        assert exec_.date_execution is not None

    def test_workflow_obligatoire(self, session):
        exec_ = Execution(status="EN_COURS")
        session.add(exec_)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_history_json_optionnel(self, session, workflow_simple):
        exec_ = Execution(workflow_id=workflow_simple.id_workflow)
        session.add(exec_)
        session.commit()
        assert exec_.history_json is None

    def test_history_json_avec_donnees(self, session, workflow_simple):
        history = [{"role": "user", "content": "Hello"}]
        exec_ = Execution(workflow_id=workflow_simple.id_workflow, history_json=history)
        session.add(exec_)
        session.commit()
        assert exec_.history_json == history

    def test_outputs_json_avec_donnees(self, session, workflow_simple):
        outputs = {"1": {"contenu": "rÃ©sultat agent 1"}}
        exec_ = Execution(workflow_id=workflow_simple.id_workflow, outputs_json=outputs)
        session.add(exec_)
        session.commit()
        assert exec_.outputs_json == outputs


class TestExecutionStatus:
    """VÃ©rifie la contrainte sur le statut."""

    @pytest.mark.parametrize("status", ["EN_COURS", "TERMINE", "ERREUR"])
    def test_status_valide(self, session, workflow_simple, status):
        exec_ = Execution(workflow_id=workflow_simple.id_workflow, status=status)
        session.add(exec_)
        session.commit()
        assert exec_.status == status

    @pytest.mark.parametrize("status", ["EN_ATTENTE", "ANNULE", ""])
    def test_status_invalide(self, session, workflow_simple, status):
        exec_ = Execution(workflow_id=workflow_simple.id_workflow, status=status)
        session.add(exec_)
        with pytest.raises(IntegrityError):
            session.commit()


class TestExecutionRelations:
    """VÃ©rifie les relations de Execution."""

    def test_relation_workflow(self, session, workflow_simple):
        exec_ = Execution(workflow_id=workflow_simple.id_workflow)
        session.add(exec_)
        session.commit()
        assert exec_.workflow.nom == workflow_simple.nom

    def test_cascade_messages(self, session, execution_en_cours):
        from back.models.message_model import Message
        msg = Message(contenu="Test", type="system", expediteur="system",
                      execution_id=execution_en_cours.id_execution)
        session.add(msg)
        session.commit()

        session.delete(execution_en_cours)
        session.commit()

        assert session.query(Message).count() == 0

    def test_cascade_resultat(self, session, execution_en_cours):
        res = Resultat(contenu_final="RÃ©sultat final",
                       execution_id=execution_en_cours.id_execution)
        session.add(res)
        session.commit()

        session.delete(execution_en_cours)
        session.commit()

        assert session.query(Resultat).count() == 0


# ---------------------------------------------------------------------------
# Tests Resultat
# ---------------------------------------------------------------------------

class TestResultatCreation:
    """Tests de crÃ©ation et persistance."""

    def test_creation_valide(self, session, execution_en_cours):
        res = Resultat(
            contenu_final="Voici le rÃ©sultat final.",
            execution_id=execution_en_cours.id_execution,
        )
        session.add(res)
        session.commit()

        result = session.query(Resultat).get(res.id_resultat)
        assert result.contenu_final == "Voici le rÃ©sultat final."

    def test_date_generation_auto(self, session, execution_en_cours):
        res = Resultat(contenu_final="OK", execution_id=execution_en_cours.id_execution)
        session.add(res)
        session.commit()
        assert res.date_generation is not None

    def test_contenu_final_obligatoire(self, session, execution_en_cours):
        res = Resultat(execution_id=execution_en_cours.id_execution)
        session.add(res)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_execution_id_obligatoire(self, session):
        res = Resultat(contenu_final="Contenu sans exÃ©cution")
        session.add(res)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_unicite_par_execution(self, session, execution_en_cours):
        """Un seul Resultat par Execution (contrainte unique)."""
        res1 = Resultat(contenu_final="Premier", execution_id=execution_en_cours.id_execution)
        res2 = Resultat(contenu_final="Doublon", execution_id=execution_en_cours.id_execution)
        session.add_all([res1, res2])
        with pytest.raises(IntegrityError):
            session.commit()

    def test_relation_execution(self, session, execution_en_cours):
        res = Resultat(contenu_final="Liaison OK",
                       execution_id=execution_en_cours.id_execution)
        session.add(res)
        session.commit()
        assert res.execution.id_execution == execution_en_cours.id_execution
