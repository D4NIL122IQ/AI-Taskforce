# tests/rag/test_rag_service.py
"""
Tests unitaires pour DocumentService et RAGService.

STRATÉGIE :
  - Tous les appels réseau (Pléiade) sont mockés → zéro appel réel
  - ChromaDB est remplacé par un mock en mémoire
  - DocumentService utilise tmp_path (pytest) pour les fichiers
  - SQLAlchemy est mocké (pas de BDD réelle nécessaire)

LANCER :
  pytest tests/test_rag_service.py -v
"""

import os
import json
import pytest
from unittest.mock import MagicMock, patch, mock_open


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES PARTAGÉES
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def db_session():
    """Session SQLAlchemy mockée."""
    session = MagicMock()
    session.query.return_value.filter.return_value.all.return_value = []
    session.query.return_value.filter.return_value.first.return_value = None
    return session


@pytest.fixture
def fake_embedding():
    """Vecteur d'embedding factice de dimension 10."""
    return [0.1] * 10


@pytest.fixture
def mock_pleiade_embedding(fake_embedding):
    """Mock de requests.post pour l'API embeddings de Pléiade."""
    with patch("backend.services.rag_service.requests.post") as mock_post:
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "data": [{"embedding": fake_embedding}]
        }
        mock_post.return_value = response
        yield mock_post


@pytest.fixture
def mock_chroma_collection():
    """Collection ChromaDB mockée en mémoire."""
    col = MagicMock()
    col.query.return_value = {
        "documents": [["chunk 1 pertinent", "chunk 2 pertinent"]],
        "distances": [[0.1, 0.2]],
    }
    return col


@pytest.fixture
def rag_service(mock_chroma_collection):
    """Instance RAGService avec collection ChromaDB mockée."""
    from backend.services.rag_service import RAGService
    svc = RAGService()
    svc._collection = mock_chroma_collection
    return svc


# ══════════════════════════════════════════════════════════════════════════════
# TESTS : RAGService — extraction de texte
# ══════════════════════════════════════════════════════════════════════════════

class TestExtraireTexte:

    def test_extrait_txt(self, tmp_path, rag_service):
        f = tmp_path / "doc.txt"
        f.write_text("Bonjour le monde", encoding="utf-8")
        result = rag_service._extraire_texte(str(f))
        assert result == "Bonjour le monde"

    def test_extrait_md(self, tmp_path, rag_service):
        f = tmp_path / "doc.md"
        f.write_text("# Titre\nContenu markdown", encoding="utf-8")
        result = rag_service._extraire_texte(str(f))
        assert "Contenu markdown" in result

    def test_fichier_inexistant_leve_erreur(self, rag_service):
        with pytest.raises(FileNotFoundError):
            rag_service._extraire_texte("/chemin/inexistant/fichier.txt")

    def test_format_non_supporte_leve_erreur(self, tmp_path, rag_service):
        f = tmp_path / "doc.xlsx"
        f.write_bytes(b"fake xlsx content")
        with pytest.raises(ValueError, match="non supporté"):
            rag_service._extraire_texte(str(f))
    #A FAIRE


    def test_extrait_pdf(self, tmp_path, rag_service):
        """Mock PyPDF2 pour tester l'extraction PDF sans vrai fichier PDF."""
        f = tmp_path / "doc.pdf"
        f.write_bytes(b"fake pdf")
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Contenu du PDF"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        with patch("backend.services.rag_service.PdfReader", return_value=mock_reader):
            result = rag_service._extraire_texte(str(f))
        assert result == "Contenu du PDF"

# ══════════════════════════════════════════════════════════════════════════════
# TESTS : RAGService — découpage en chunks
# ══════════════════════════════════════════════════════════════════════════════

class TestDecoupeEnChunks:

    def test_texte_court_donne_un_seul_chunk(self, rag_service):
        texte = "mot " * 10
        chunks = rag_service._decouper_en_chunks(texte)
        assert len(chunks) == 1

    def test_texte_long_donne_plusieurs_chunks(self, rag_service):
        # 1200 mots → avec CHUNK_SIZE=500 et CHUNK_OVERLAP=50 → 3+ chunks
        texte = "mot " * 1200
        chunks = rag_service._decouper_en_chunks(texte)
        assert len(chunks) > 1

    def test_chunks_non_vides(self, rag_service):
        texte = "un deux trois quatre cinq " * 200
        chunks = rag_service._decouper_en_chunks(texte)
        assert all(c.strip() for c in chunks)

    def test_texte_vide_retourne_liste_vide(self, rag_service):
        chunks = rag_service._decouper_en_chunks("")
        assert chunks == []

    def test_overlap_present(self, rag_service):
        """Vérifie que le dernier mot du chunk N apparaît dans le chunk N+1."""
        # Forcer des petits chunks pour le test
        original_size = rag_service.__class__.__module__
        import backend.services.rag_service as mod
        original_chunk_size = mod.CHUNK_SIZE
        original_overlap = mod.CHUNK_OVERLAP
        mod.CHUNK_SIZE = 5
        mod.CHUNK_OVERLAP = 2
        try:
            texte = "A B C D E F G H I J K L"
            chunks = rag_service._decouper_en_chunks(texte)
            if len(chunks) >= 2:
                # Dernier mot du chunk 0 doit être dans chunk 1
                dernier_mot_chunk0 = chunks[0].split()[-1]
                assert dernier_mot_chunk0 in chunks[1]
        finally:
            mod.CHUNK_SIZE = original_chunk_size
            mod.CHUNK_OVERLAP = original_overlap


# ══════════════════════════════════════════════════════════════════════════════
# TESTS : RAGService — embeddings via Pléiade
# ══════════════════════════════════════════════════════════════════════════════

class TestGenererEmbedding:

    def test_retourne_vecteur(self, rag_service, mock_pleiade_embedding, fake_embedding):
        result = rag_service._generer_embedding("texte de test")
        assert result == fake_embedding

    def test_appel_api_avec_bon_modele(self, rag_service, mock_pleiade_embedding):
        rag_service._generer_embedding("test")
        call_kwargs = mock_pleiade_embedding.call_args
        payload = call_kwargs[1]["json"]
        assert "model" in payload
        assert "input" in payload
        assert payload["input"] == "test"

    def test_erreur_api_leve_runtime_error(self, rag_service):
        with patch("backend.services.rag_service.requests.post") as mock_post:
            response = MagicMock()
            response.status_code = 401
            response.text = "Unauthorized"
            mock_post.return_value = response
            with pytest.raises(RuntimeError, match="401"):
                rag_service._generer_embedding("test")

    def test_header_authorization_present(self, rag_service, mock_pleiade_embedding):
        rag_service._generer_embedding("test")
        headers = mock_pleiade_embedding.call_args[1]["headers"]
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer")


# ══════════════════════════════════════════════════════════════════════════════
# TESTS : RAGService — indexation complète
# ══════════════════════════════════════════════════════════════════════════════

class TestIndexerDocument:

    def test_indexation_txt(self, tmp_path, rag_service, mock_pleiade_embedding):
        f = tmp_path / "doc.txt"
        f.write_text("mot " * 600, encoding="utf-8")  # assez pour 1+ chunks
        nb_chunks = rag_service.indexer_document(
            doc_id=1, agent_id=10, chemin_fichier=str(f)
        )
        assert nb_chunks > 0
        rag_service.collection.add.assert_called_once()

    def test_ids_chunks_corrects(self, tmp_path, rag_service, mock_pleiade_embedding):
        f = tmp_path / "doc.txt"
        f.write_text("a " * 600, encoding="utf-8")
        rag_service.indexer_document(doc_id=5, agent_id=2, chemin_fichier=str(f))
        call_args = rag_service.collection.add.call_args[1]
        assert all(id_.startswith("doc_5_chunk_") for id_ in call_args["ids"])

    def test_metadatas_contiennent_agent_id(self, tmp_path, rag_service, mock_pleiade_embedding):
        f = tmp_path / "doc.txt"
        f.write_text("b " * 600, encoding="utf-8")
        rag_service.indexer_document(doc_id=3, agent_id=7, chemin_fichier=str(f))
        call_args = rag_service.collection.add.call_args[1]
        assert all(m["agent_id"] == 7 for m in call_args["metadatas"])

    def test_document_vide_retourne_zero(self, tmp_path, rag_service, mock_pleiade_embedding):
        f = tmp_path / "vide.txt"
        f.write_text("", encoding="utf-8")
        nb = rag_service.indexer_document(doc_id=99, agent_id=1, chemin_fichier=str(f))
        assert nb == 0
        rag_service.collection.add.assert_not_called()


# ══════════════════════════════════════════════════════════════════════════════
# TESTS : RAGService — recherche
# ══════════════════════════════════════════════════════════════════════════════

class TestRechercher:

    def test_retourne_liste_chunks(self, rag_service, mock_pleiade_embedding):
        chunks = rag_service.rechercher(agent_id=1, question="question test")
        assert isinstance(chunks, list)
        assert len(chunks) == 2  # mock retourne 2 chunks
        assert chunks[0] == "chunk 1 pertinent"

    def test_filtre_par_agent_id(self, rag_service, mock_pleiade_embedding):
        rag_service.rechercher(agent_id=42, question="test")
        call_kwargs = rag_service.collection.query.call_args[1]
        assert call_kwargs["where"] == {"agent_id": 42}

    def test_question_vide_retourne_liste_vide(self, rag_service):
        result = rag_service.rechercher(agent_id=1, question="   ")
        assert result == []
        rag_service.collection.query.assert_not_called()

    def test_top_k_transmis(self, rag_service, mock_pleiade_embedding):
        rag_service.rechercher(agent_id=1, question="test", top_k=3)
        call_kwargs = rag_service.collection.query.call_args[1]
        assert call_kwargs["n_results"] == 3


# ══════════════════════════════════════════════════════════════════════════════
# TESTS : RAGService — contexte_pour_prompt
# ══════════════════════════════════════════════════════════════════════════════

class TestContextePourPrompt:

    def test_retourne_chaine_avec_chunks(self, rag_service, mock_pleiade_embedding):
        ctx = rag_service.contexte_pour_prompt(agent_id=1, question="ma question")
        assert "chunk 1 pertinent" in ctx
        assert "Contexte documentaire" in ctx

    def test_retourne_vide_si_aucun_chunk(self, rag_service, mock_pleiade_embedding):
        rag_service.collection.query.return_value = {"documents": [[]], "distances": [[]]}
        ctx = rag_service.contexte_pour_prompt(agent_id=1, question="question")
        assert ctx == ""

    def test_format_avec_extraits_numerotes(self, rag_service, mock_pleiade_embedding):
        ctx = rag_service.contexte_pour_prompt(agent_id=1, question="test")
        assert "[Extrait 1]" in ctx
        assert "[Extrait 2]" in ctx


# ══════════════════════════════════════════════════════════════════════════════
# TESTS : RAGService — suppression
# ══════════════════════════════════════════════════════════════════════════════

class TestSuppression:

    def test_supprimer_document_appelle_chroma_delete(self, rag_service):
        rag_service.supprimer_document(doc_id=10)
        rag_service.collection.delete.assert_called_once_with(where={"doc_id": 10})

    def test_supprimer_agent_appelle_chroma_delete(self, rag_service):
        rag_service.supprimer_agent(agent_id=5)
        rag_service.collection.delete.assert_called_once_with(where={"agent_id": 5})


# ══════════════════════════════════════════════════════════════════════════════
# TESTS : DocumentService
# ══════════════════════════════════════════════════════════════════════════════

class TestDocumentService:

    def _make_service(self, db_session):
        with patch("backend.services.document_service.os.makedirs"):
            from backend.services.document_service import DocumentService
            return DocumentService(db=db_session)

    def test_sauvegarder_cree_fichier(self, db_session, tmp_path):
        with patch("backend.services.document_service.UPLOAD_DIR", str(tmp_path)), \
             patch("backend.services.document_service.os.makedirs"):
            from backend.services.document_service import DocumentService
            svc = DocumentService(db=db_session)

            fake_doc = MagicMock()
            fake_doc.id_document = 1
            db_session.query.return_value.filter.return_value.first.return_value = fake_doc
            db_session.refresh.side_effect = lambda x: None

            svc.sauvegarder(agent_id=1, filename="test.txt", file_bytes=b"contenu")
            db_session.add.assert_called_once()
            db_session.commit.assert_called_once()

    def test_sauvegarder_extension_invalide(self, db_session):
        svc = self._make_service(db_session)
        with pytest.raises(ValueError, match="non supportée"):
            svc.sauvegarder(agent_id=1, filename="image.jpg", file_bytes=b"data")

    def test_sauvegarder_fichier_vide(self, db_session):
        svc = self._make_service(db_session)
        with pytest.raises(ValueError, match="vide"):
            svc.sauvegarder(agent_id=1, filename="doc.txt", file_bytes=b"")

    def test_lister_appelle_query_filtre(self, db_session):
        svc = self._make_service(db_session)
        svc.lister(agent_id=3)
        db_session.query.assert_called_once()

    def test_supprimer_retourne_false_si_doc_inexistant(self, db_session):
        db_session.query.return_value.filter.return_value.first.return_value = None
        svc = self._make_service(db_session)
        result = svc.supprimer(doc_id=999)
        assert result is False

    def test_supprimer_retourne_true_et_commit(self, db_session, tmp_path):
        fake_doc = MagicMock()
        fake_doc.id_document = 1
        fake_doc.chemin = str(tmp_path / "fichier.txt")
        db_session.query.return_value.filter.return_value.first.return_value = fake_doc

        with patch("backend.services.document_service.os.path.exists", return_value=False), \
             patch("backend.services.document_service.RAGService") as MockRAG:
            MockRAG.return_value.supprimer_document.return_value = None
            svc = self._make_service(db_session)
            result = svc.supprimer(doc_id=1)

        assert result is True
        db_session.delete.assert_called_once_with(fake_doc)
        db_session.commit.assert_called_once()