# backend/services/rag_service.py
"""
RAGService — Retrieval-Augmented Generation pour AI Taskforce.

PIPELINE COMPLET :
┌──────────────┐ → ┌──────────────┐ → ┌──────────────┐ → ┌──────────────┐ → ┌──────────────┐
│   Fichier    │   │ Extraction   │   │   Chunks     │   │ Embeddings   │   │  ChromaDB    │
│ (pdf/txt…)   │   │   texte      │   │ (chunk_size) │   │  (Ollama)    │   │ + metadata   │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘

  Lors d'une requête :
    Question utilisateur → Embedding (Ollama) → Retrieval (Similarity + MMR) → Top-K chunks → Post-traitement (filtrage + extraction + reranking) → LLM → Réponse
DÉPENDANCES EXTERNES :
  pip install chromadb langchain-text-splitters PyPDF2 langchain-ollama
  ollama pull nomic-embed-text # le moteur d'embedding

CONFIGURATION (.env) :
  TOKEN_PLEIADE=<votre_token>
  CHROMA_DIR=chroma_db       ← dossier de persistance ChromaDB (défaut)
  CHUNK_SIZE=500              ← taille des chunks en mots (défaut)
  CHUNK_OVERLAP=50            ← overlap entre chunks (défaut)
  EMBEDDING_MODEL=nomic-embed-text:latest  ← modèle Pléiade pour les embeddings

PIPELINE COMPLET :
  Fichier → Chunks → Embeddings → Base vectorielle (Chroma)

Utilise une base Chroma persistante avec embeddings locaux.
Les documents sont filtrés par agent_id via les métadonnées.
"""

import os
from typing import List
from dotenv import load_dotenv
from pypdf import PdfReader


from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────

CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_db")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

EMBEDDING_MODEL = "nomic-embed-text"


class RAGService:
    """
    Service RAG : indexation et recherche de documents via embeddings.

    Implémentation basée sur Chroma + LangChain.
    """

    def __init__(self):
        self._vectordb = None  # lazy loading

    # ──────────────────────────────────────────────────────────────────────────
    # PROPRIÉTÉ : base vectorielle (lazy)
    # ──────────────────────────────────────────────────────────────────────────
    @property
    def vectordb(self):
        if self._vectordb is None:
            embedding = OllamaEmbeddings(model=EMBEDDING_MODEL)

            self._vectordb = Chroma(
                persist_directory=CHROMA_DIR,
                embedding_function=embedding
            )

        return self._vectordb

    # ──────────────────────────────────────────────────────────────────────────
    # ÉTAPE 1 : EXTRACTION DU TEXTE
    # ──────────────────────────────────────────────────────────────────────────
    def _extraire_texte(self, chemin: str) -> str:
        if not os.path.exists(chemin):
            raise FileNotFoundError(f"Fichier introuvable : {chemin}")

        ext = os.path.splitext(chemin)[1].lower()

        if ext in (".txt", ".md"):
            return open(chemin, "r", encoding="utf-8").read()

        elif ext == ".pdf":
            reader = PdfReader(chemin)
            return "\n".join(page.extract_text() or "" for page in reader.pages)

        elif ext == ".docx":
            from docx import Document as DocxDocument
            doc = DocxDocument(chemin)
            return "\n".join(p.text for p in doc.paragraphs)

        else:
            raise ValueError(f"Format non supporté pour le RAG : {ext}")

    # ──────────────────────────────────────────────────────────────────────────
    # ÉTAPE 2 : DÉCOUPAGE EN CHUNKS
    # ──────────────────────────────────────────────────────────────────────────
    def _decouper_en_chunks(self, texte: str) -> List[Document]:
        """
        Découpe le texte en segments avec overlap pour préserver le contexte.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""]
        )

        return splitter.create_documents([texte])

    # ──────────────────────────────────────────────────────────────────────────
    # ÉTAPE 3 : INDEXATION
    # ──────────────────────────────────────────────────────────────────────────
    def indexer_document(self, doc_id: int, agent_id: int, chemin_fichier: str) -> int:
        print(f"[RAGService] Indexation doc_id={doc_id}, agent_id={agent_id}...")

        # 1. Extraction
        texte = self._extraire_texte(chemin_fichier)

        if not texte.strip():
            print("[RAGService] ⚠ Document vide.")
            return 0

        # 2. Découpage
        documents = self._decouper_en_chunks(texte)

        # 3. Ajout des métadonnées
        for i, doc in enumerate(documents):
            doc.metadata = {
                "doc_id": doc_id,
                "agent_id": agent_id,
                "chunk_index": i,
                "chemin": chemin_fichier
            }

        # 4. Stockage
        self.vectordb.add_documents(documents)

        print(f"[RAGService] {len(documents)} chunks indexés.")
        return len(documents)

    # ──────────────────────────────────────────────────────────────────────────
    # RECHERCHE
    # ──────────────────────────────────────────────────────────────────────────

    def rechercher(self, agent_id: int, question: str, top_k: int = 5, use_post: bool = False) -> List[str]:
        if not question.strip():
            return []

        # Retriever MMR
        base_retriever = self.vectordb.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": top_k,
                "fetch_k": 30,
                "lambda_mult": 0.5,
                "filter": {"agent_id": agent_id}
            }
        )

        if use_post:
            docs = self.post_traitement(base_retriever, question)
        else:
            docs = base_retriever.invoke(question)

        return [doc.page_content for doc in docs]


    def post_traitement(self, retriever, question: str) -> List:
        """
        Pipeline LangChain :
        1. Filtrage (doublons)
        2. Compression LLM = extraction + reranking
        """

        # recuperation
        docs = retriever.invoke(question)

        # =============================
        # 2. Filtrage doublons
        unique_docs = []
        seen = set()

        for doc in docs:
            content = doc.page_content.strip()
            if content not in seen:
                seen.add(content)
                unique_docs.append(doc)

        if not unique_docs:
            return []

        # =============================
        # 3. Extraction + Reranking LLM
        # =============================
        #compressor = LLMChainExtractor.from_llm(self.llm)

        #compression_retriever = ContextualCompressionRetriever(
        #   base_retriever=lambda q: unique_docs,  # on injecte nos docs filtrés
        #   compressor=compressor
        #)

        #compressed_docs = compression_retriever.invoke(question)

        return unique_docs
    # ──────────────────────────────────────────────────────────────────────────
    # CONTEXTE POUR PROMPT
    # ──────────────────────────────────────────────────────────────────────────
    def contexte_pour_prompt(self, agent_id: int, question: str, top_k: int = 5) -> str:
        
        from backend.services.document_service import DocumentService
        from backend.appDatabase.database import get_db

        docService = DocumentService(next(get_db()))
        list_docs = docService.lister(agent_id=agent_id)
        for doc in list_docs:
            self.indexer_document(doc_id= doc.id_document,
                                   agent_id= agent_id,
                                   chemin_fichier= doc.chemin)
            
        chunks = self.rechercher(agent_id, question, top_k)

        if not chunks:
            return ""

        lignes = ["=== Contexte documentaire pertinent ==="]
        for i, chunk in enumerate(chunks, 1):
            lignes.append(f"[Extrait {i}]\n{chunk}")
        lignes.append("=" * 40)

        return "\n\n".join(lignes)

    # ──────────────────────────────────────────────────────────────────────────
    # SUPPRESSION
    # ──────────────────────────────────────────────────────────────────────────
    def supprimer_document(self, doc_id: int):
        self.vectordb._collection.delete(where={"doc_id": doc_id})

    def supprimer_agent(self, agent_id: int):
        self.vectordb._collection.delete(where={"agent_id": agent_id})