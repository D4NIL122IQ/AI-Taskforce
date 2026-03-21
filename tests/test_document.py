import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import back.models.agent
import back.models.message
import back.models.workflow
import back.models.etape
import back.models.execution

import pytest
from datetime import datetime, timezone
from back.models.document import Document


@pytest.fixture
def document_valide():
    return Document(
        nom_fichier="rapport.pdf",
        type_fichier="pdf",
        chemin="/tmp/rapport.pdf",
        agent_id=1
    )


class TestDocumentInit:

    def test_attributs_de_base(self, document_valide):
        assert document_valide.nom_fichier  == "rapport.pdf"
        assert document_valide.type_fichier == "pdf"
        assert document_valide.chemin       == "/tmp/rapport.pdf"
        assert document_valide.agent_id     == 1

    def test_date_upload_auto(self, document_valide):
        assert isinstance(document_valide.date_upload, datetime)

    def test_date_upload_explicite(self):
        date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        doc  = Document("f.txt", "txt", "/tmp/f.txt", agent_id=1, date_upload=date)
        assert doc.date_upload == date

    @pytest.mark.parametrize("type_valide", ["pdf", "txt", "docx", "md"])
    def test_types_valides(self, type_valide):
        doc = Document("fichier", type_valide, "/tmp/f", agent_id=1)
        assert doc.type_fichier == type_valide


class TestDocumentInitErreurs:

    def test_nom_vide(self):
        with pytest.raises(ValueError, match="Nom de fichier vide"):
            Document("", "pdf", "/tmp/f.pdf", agent_id=1)

    def test_chemin_vide(self):
        with pytest.raises(ValueError, match="Chemin vide"):
            Document("f.pdf", "pdf", "", agent_id=1)

    @pytest.mark.parametrize("type_invalide", ["xls", "jpg", "zip", ""])
    def test_type_invalide(self, type_invalide):
        with pytest.raises(ValueError, match="Type de fichier non supporté"):
            Document("f", type_invalide, "/tmp/f", agent_id=1)


class TestDocumentLire:

    def test_lire_fichier_absent(self, document_valide):
        with pytest.raises(IOError, match="Fichier introuvable"):
            document_valide.lire()

    def test_lire_txt(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("contenu texte", encoding="utf-8")
        doc = Document("test.txt", "txt", str(f), agent_id=1)
        assert doc.lire() == "contenu texte"

    def test_lire_md(self, tmp_path):
        f = tmp_path / "readme.md"
        f.write_text("# Titre", encoding="utf-8")
        doc = Document("readme.md", "md", str(f), agent_id=1)
        assert doc.lire() == "# Titre"


class TestDocumentAnalyser:

    def test_analyser_retourne_chunks(self, tmp_path):
        f = tmp_path / "doc.txt"
        f.write_text(" ".join([f"mot{i}" for i in range(100)]), encoding="utf-8")
        doc    = Document("doc.txt", "txt", str(f), agent_id=1)
        chunks = doc.analyser()
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert "text"        in chunks[0]
        assert "source"      in chunks[0]
        assert "chunk_index" in chunks[0]

    def test_analyser_source_correcte(self, tmp_path):
        f = tmp_path / "source.txt"
        f.write_text("du texte", encoding="utf-8")
        doc    = Document("source.txt", "txt", str(f), agent_id=1)
        chunks = doc.analyser()
        assert chunks[0]["source"] == "source.txt"


class TestDocumentToDict:

    def test_cles_presentes(self, document_valide):
        d = document_valide.toDict()
        assert set(d.keys()) == {
            "id_document", "nom_fichier", "type_fichier",
            "chemin", "date_upload", "agent_id"
        }

    def test_valeurs_correctes(self, document_valide):
        d = document_valide.toDict()
        assert d["nom_fichier"]  == "rapport.pdf"
        assert d["type_fichier"] == "pdf"
        assert d["agent_id"]     == 1

    def test_repr(self, document_valide):
        assert "pdf"         in repr(document_valide)
        assert "rapport.pdf" in repr(document_valide)