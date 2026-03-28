import pytest
from sqlalchemy.exc import IntegrityError
from back.models.agent_model import Agent


class TestAgentCreation:
    """Tests de crÃ©ation et de persistance basique."""

    def test_creation_minimale(self, session):
        agent = Agent(nom="MonAgent", modele="Openai")
        session.add(agent)
        session.commit()

        result = session.query(Agent).filter_by(nom="MonAgent").first()
        assert result is not None
        assert result.modele == "Openai"

    def test_valeurs_par_defaut(self, session):
        agent = Agent(nom="AgentDefaut", modele="Mistral")
        session.add(agent)
        session.commit()

        assert agent.temperature == pytest.approx(0.7)
        assert agent.max_tokens == 1024
        assert agent.statut == "ACTIF"
        assert agent.date_creation is not None

    def test_tous_les_champs(self, session):
        agent = Agent(
            nom="AgentComplet",
            role="Analyste",
            modele="Gemini",
            temperature=0.3,
            max_tokens=2048,
            system_prompt="Tu es un expert.",
            statut="ACTIF",
        )
        session.add(agent)
        session.commit()

        result = session.query(Agent).get(agent.id_agent)
        assert result.role == "Analyste"
        assert result.system_prompt == "Tu es un expert."
        assert result.max_tokens == 2048

    def test_nom_obligatoire(self, session):
        agent = Agent(modele="Openai")
        session.add(agent)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_modele_obligatoire(self, session):
        agent = Agent(nom="SansModele")
        session.add(agent)
        with pytest.raises(IntegrityError):
            session.commit()


class TestAgentModeles:
    """VÃ©rifie que tous les modÃ¨les autorisÃ©s sont acceptÃ©s."""

    @pytest.mark.parametrize("modele", ["Openai", "Ollama", "Mistral", "DeepSeek", "Anthropic", "Gemini"])
    def test_modele_valide(self, session, modele):
        agent = Agent(nom=f"Agent_{modele}", modele=modele)
        session.add(agent)
        session.commit()
        assert agent.id_agent is not None

    def test_modele_invalide(self, session):
        agent = Agent(nom="AgentInvalide", modele="GPT-99")
        session.add(agent)
        with pytest.raises(IntegrityError):
            session.commit()


class TestAgentTemperature:
    """VÃ©rifie les contraintes sur la tempÃ©rature."""

    @pytest.mark.parametrize("temp", [0.0, 0.5, 1.0])
    def test_temperature_valide(self, session, temp):
        agent = Agent(nom=f"Agent_temp_{temp}", modele="Openai", temperature=temp)
        session.add(agent)
        session.commit()
        assert agent.temperature == pytest.approx(temp)

    @pytest.mark.parametrize("temp", [-0.1, 1.1, 2.0])
    def test_temperature_invalide(self, session, temp):
        agent = Agent(nom=f"Agent_temp_invalide_{temp}", modele="Openai", temperature=temp)
        session.add(agent)
        with pytest.raises(IntegrityError):
            session.commit()


class TestAgentMaxTokens:
    """VÃ©rifie les contraintes sur max_tokens."""

    @pytest.mark.parametrize("tokens", [1, 1024, 8192])
    def test_max_tokens_valide(self, session, tokens):
        agent = Agent(nom=f"Agent_tokens_{tokens}", modele="Openai", max_tokens=tokens)
        session.add(agent)
        session.commit()
        assert agent.max_tokens == tokens

    @pytest.mark.parametrize("tokens", [0, -1, 8193])
    def test_max_tokens_invalide(self, session, tokens):
        agent = Agent(nom=f"Agent_tokens_invalide_{tokens}", modele="Openai", max_tokens=tokens)
        session.add(agent)
        with pytest.raises(IntegrityError):
            session.commit()


class TestAgentStatut:
    """VÃ©rifie les contraintes sur le statut."""

    @pytest.mark.parametrize("statut", ["ACTIF", "INTERROMPU"])
    def test_statut_valide(self, session, statut):
        agent = Agent(nom=f"Agent_{statut}", modele="Openai", statut=statut)
        session.add(agent)
        session.commit()
        assert agent.statut == statut

    def test_statut_invalide(self, session):
        agent = Agent(nom="AgentStatutInvalide", modele="Openai", statut="SUPPRIME")
        session.add(agent)
        with pytest.raises(IntegrityError):
            session.commit()


class TestAgentRelations:
    """VÃ©rifie les relations cascade."""

    def test_suppression_cascade_documents(self, session, agent_actif):
        from back.models.document_model import Document
        doc = Document(nom_fichier="fichier.pdf", type_fichier="pdf",
                       chemin="/tmp/fichier.pdf", agent_id=agent_actif.id_agent)
        session.add(doc)
        session.commit()

        session.delete(agent_actif)
        session.commit()

        assert session.query(Document).count() == 0

    def test_suppression_cascade_messages(self, session, agent_actif, execution_en_cours):
        from back.models.message_model import Message
        msg = Message(contenu="Hello", type="user_input",
                      expediteur="user", execution_id=execution_en_cours.id_execution)
        session.add(msg)
        session.commit()

        count_before = session.query(Message).count()
        assert count_before == 1
