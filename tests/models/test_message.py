import pytest
from sqlalchemy.exc import IntegrityError
from back.models.message_model import Message


class TestMessageCreation:
    """Tests de création et persistance."""

    def test_creation_valide(self, session, execution_en_cours):
        msg = Message(
            contenu="Bonjour, comment puis-je aider ?",
            type="user_input",
            expediteur="utilisateur@example.com",
            execution_id=execution_en_cours.id_execution,
        )
        session.add(msg)
        session.commit()

        result = session.query(Message).get(msg.id)
        assert result is not None
        assert result.contenu == "Bonjour, comment puis-je aider ?"

    def test_date_creation_auto(self, session, execution_en_cours):
        msg = Message(contenu="Test", type="system", expediteur="system",
                      execution_id=execution_en_cours.id_execution)
        session.add(msg)
        session.commit()
        assert msg.date_creation is not None

    def test_execution_optionnelle(self, session):
        """Un message peut exister sans être rattaché à une exécution."""
        msg = Message(contenu="Message libre", type="system", expediteur="system")
        session.add(msg)
        session.commit()
        assert msg.id is not None
        assert msg.execution_id is None

    def test_contenu_obligatoire(self, session):
        msg = Message(type="system", expediteur="system")
        session.add(msg)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_type_obligatoire(self, session):
        msg = Message(contenu="Sans type", expediteur="system")
        session.add(msg)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_expediteur_obligatoire(self, session):
        msg = Message(contenu="Sans expéditeur", type="system")
        session.add(msg)
        with pytest.raises(IntegrityError):
            session.commit()


class TestMessageTypes:
    """Vérifie la contrainte CHECK sur le champ type."""

    @pytest.mark.parametrize("type_msg", ["user_input", "agent_response", "system"])
    def test_type_valide(self, session, type_msg):
        msg = Message(contenu="Contenu", type=type_msg, expediteur="expediteur")
        session.add(msg)
        session.commit()
        assert msg.id is not None

    @pytest.mark.parametrize("type_msg", ["erreur", "notification", "", "USER_INPUT"])
    def test_type_invalide(self, session, type_msg):
        msg = Message(contenu="Contenu", type=type_msg, expediteur="expediteur")
        session.add(msg)
        with pytest.raises(IntegrityError):
            session.commit()


class TestMessageRelations:
    """Vérifie les relations avec Execution."""

    def test_relation_execution(self, session, execution_en_cours):
        msg = Message(contenu="Lié", type="system", expediteur="system",
                      execution_id=execution_en_cours.id_execution)
        session.add(msg)
        session.commit()
        assert msg.execution.id_execution == execution_en_cours.id_execution

    def test_plusieurs_messages_par_execution(self, session, execution_en_cours):
        types = ["user_input", "agent_response", "system"]
        for i, t in enumerate(types):
            session.add(Message(contenu=f"msg {i}", type=t, expediteur="x",
                                execution_id=execution_en_cours.id_execution))
        session.commit()

        msgs = (session.query(Message)
                .filter_by(execution_id=execution_en_cours.id_execution)
                .all())
        assert len(msgs) == 3

    def test_execution_inexistante(self, session):
        msg = Message(contenu="Orphelin", type="system", expediteur="system",
                      execution_id=9999)
        session.add(msg)
        with pytest.raises(IntegrityError):
            session.commit()