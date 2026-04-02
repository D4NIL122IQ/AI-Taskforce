import pytest
from sqlalchemy.exc import IntegrityError
from backend.models.document_model import Document
from backend.models.agent_model import Agent


class TestDocumentCreation:
    """Tests de création et persistance."""

    def test_creation_valide(self, session, agent_actif):
        doc = Document(
            nom_fichier="rapport.pdf",
            type_fichier="pdf",
            chemin="/data/rapport.pdf",
            agent_id=agent_actif.id_agent,
        )
        session.add(doc)
        session.commit()

        result = session.query(Document).filter_by(nom_fichier="rapport.pdf").first()
        assert result is not None
        assert result.chemin == "/data/rapport.pdf"

    def test_date_upload_auto(self, session, agent_actif):
        doc = Document(nom_fichier="auto.txt", type_fichier="txt",
                       chemin="/tmp/auto.txt", agent_id=agent_actif.id_agent)
        session.add(doc)
        session.commit()
        assert doc.date_upload is not None

    def test_nom_fichier_obligatoire(self, session, agent_actif):
        doc = Document(type_fichier="pdf", chemin="/tmp/x.pdf",
                       agent_id=agent_actif.id_agent)
        session.add(doc)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_chemin_obligatoire(self, session, agent_actif):
        doc = Document(nom_fichier="sans_chemin.pdf", type_fichier="pdf",
                       agent_id=agent_actif.id_agent)
        session.add(doc)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_agent_id_obligatoire(self, session):
        doc = Document(nom_fichier="orphelin.pdf", type_fichier="pdf",
                       chemin="/tmp/orphelin.pdf")
        session.add(doc)
        with pytest.raises(IntegrityError):
            session.commit()


class TestDocumentTypesFichier:
    """Vérifie la contrainte sur les types de fichiers autorisés."""

    @pytest.mark.parametrize("type_f", ["pdf", "txt", "docx", "md"])
    def test_type_valide(self, session, agent_actif, type_f):
        doc = Document(
            nom_fichier=f"fichier.{type_f}",
            type_fichier=type_f,
            chemin=f"/tmp/fichier.{type_f}",
            agent_id=agent_actif.id_agent,
        )
        session.add(doc)
        session.commit()
        assert doc.id_document is not None

    @pytest.mark.parametrize("type_f", ["xlsx", "csv", "png", "mp4", ""])
    def test_type_invalide(self, session, agent_actif, type_f):
        doc = Document(
            nom_fichier="invalide",
            type_fichier=type_f,
            chemin="/tmp/invalide",
            agent_id=agent_actif.id_agent,
        )
        session.add(doc)
        with pytest.raises(IntegrityError):
            session.commit()


class TestDocumentRelation:
    """Vérifie la relation avec Agent."""

    def test_relation_agent(self, session, agent_actif):
        doc = Document(nom_fichier="rel.pdf", type_fichier="pdf",
                       chemin="/tmp/rel.pdf", agent_id=agent_actif.id_agent)
        session.add(doc)
        session.commit()

        assert doc.agent.nom == agent_actif.nom

    def test_agent_inexistant(self, session):
        doc = Document(nom_fichier="orphelin.pdf", type_fichier="pdf",
                       chemin="/tmp/orphelin.pdf", agent_id=9999)
        session.add(doc)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_plusieurs_documents_par_agent(self, session, agent_actif):
        for i in range(3):
            doc = Document(
                nom_fichier=f"doc_{i}.pdf",
                type_fichier="pdf",
                chemin=f"/tmp/doc_{i}.pdf",
                agent_id=agent_actif.id_agent,
            )
            session.add(doc)
        session.commit()

        assert len(agent_actif.documents) == 3
