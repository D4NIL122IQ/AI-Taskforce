import pytest
from sqlalchemy.exc import IntegrityError
from back.models.utilisateur_model import Utilisateur


class TestUtilisateurCreation:

    def test_creation_valide(self, session):
        u = Utilisateur(nom="Alice", email="alice@example.com", mot_de_passe="hashed")
        session.add(u)
        session.commit()
        result = session.query(Utilisateur).filter_by(email="alice@example.com").first()
        assert result is not None
        assert result.nom == "Alice"

    def test_date_creation_auto(self, session):
        u = Utilisateur(nom="Bob", email="bob@example.com", mot_de_passe="hashed")
        session.add(u)
        session.commit()
        assert u.date_creation is not None

    def test_nom_obligatoire(self, session):
        u = Utilisateur(email="sannom@example.com", mot_de_passe="hashed")
        session.add(u)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_email_obligatoire(self, session):
        u = Utilisateur(nom="Sans Email", mot_de_passe="hashed")
        session.add(u)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_mot_de_passe_obligatoire(self, session):
        u = Utilisateur(nom="Sans MDP", email="sansmdp@example.com")
        session.add(u)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_email_unique(self, session):
        u1 = Utilisateur(nom="Eve", email="eve@example.com", mot_de_passe="h1")
        u2 = Utilisateur(nom="Eve2", email="eve@example.com", mot_de_passe="h2")
        session.add_all([u1, u2])
        with pytest.raises(IntegrityError):
            session.commit()

    def test_plusieurs_utilisateurs_emails_differents(self, session):
        u1 = Utilisateur(nom="User1", email="u1@example.com", mot_de_passe="h1")
        u2 = Utilisateur(nom="User2", email="u2@example.com", mot_de_passe="h2")
        session.add_all([u1, u2])
        session.commit()
        assert session.query(Utilisateur).count() == 2


class TestUtilisateurRelations:

    def test_relation_agents(self, session):
        from back.models.agent_model import Agent
        u = Utilisateur(nom="Carol", email="carol@example.com", mot_de_passe="h")
        session.add(u)
        session.commit()

        a = Agent(nom="MonAgent", modele="Openai", utilisateur_id=u.id_utilisateur)
        session.add(a)
        session.commit()

        assert len(u.agents) == 1
        assert u.agents[0].nom == "MonAgent"

    def test_relation_workflows(self, session):
        from back.models.workflow_model import Workflow
        u = Utilisateur(nom="Dan", email="dan@example.com", mot_de_passe="h")
        session.add(u)
        session.commit()

        wf = Workflow(nom="MonWorkflow", utilisateur_id=u.id_utilisateur)
        session.add(wf)
        session.commit()

        assert len(u.workflows) == 1
        assert u.workflows[0].nom == "MonWorkflow"

    def test_cascade_suppression_agents(self, session):
        from back.models.agent_model import Agent
        u = Utilisateur(nom="Eve", email="eve2@example.com", mot_de_passe="h")
        session.add(u)
        session.commit()

        for i in range(3):
            session.add(Agent(nom=f"Agent{i}", modele="Openai", utilisateur_id=u.id_utilisateur))
        session.commit()

        session.delete(u)
        session.commit()

        assert session.query(Agent).filter_by(utilisateur_id=u.id_utilisateur).count() == 0

    def test_cascade_suppression_workflows(self, session):
        from back.models.workflow_model import Workflow
        u = Utilisateur(nom="Frank", email="frank@example.com", mot_de_passe="h")
        session.add(u)
        session.commit()

        session.add(Workflow(nom="WF1", utilisateur_id=u.id_utilisateur))
        session.add(Workflow(nom="WF2", utilisateur_id=u.id_utilisateur))
        session.commit()

        session.delete(u)
        session.commit()

        assert session.query(Workflow).filter_by(utilisateur_id=u.id_utilisateur).count() == 0