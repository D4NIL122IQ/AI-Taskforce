# backend/services/rag_service.py
"""
RAGService — Retrieval-Augmented Generation pour AI Taskforce.

PIPELINE COMPLET :
  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │  Fichier     │ →  │   Chunks     │ →  │  Embeddings  │ →  │  ChromaDB    │
  │  (txt/pdf…)  │    │  (512 mots)  │    │  (Pléiade)   │    │  (vecteurs)  │
  └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘

  Lors d'une requête :
  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │  Question    │ →  │  Embedding   │ →  │  Top-K       │
  │  utilisateur │    │  (Pléiade)   │    │  chunks      │
  └──────────────┘    └──────────────┘    └──────────────┘

DÉPENDANCES EXTERNES :
  pip install chromadb langchain-text-splitters PyPDF2 requests

CONFIGURATION (.env) :
  TOKEN_PLEIADE=<votre_token>
  CHROMA_DIR=chroma_db       ← dossier de persistance ChromaDB (défaut)
  CHUNK_SIZE=500              ← taille des chunks en mots (défaut)
  CHUNK_OVERLAP=50            ← overlap entre chunks (défaut)
  EMBEDDING_MODEL=nomic-embed-text:latest  ← modèle Pléiade pour les embeddings

UTILISATION :
  from backend.services.rag_service import RAGService

  rag = RAGService()

  # Indexer un document
  rag.indexer_document(doc_id=1, agent_id=1, chemin_fichier="uploads/abc.pdf")

  # Rechercher les chunks pertinents
  chunks = rag.rechercher(agent_id=1, question="Quel est le chiffre d'affaires ?", top_k=5)

  # Dans Agent.executer_prompt — enrichir le contexte
  contexte = rag.contexte_pour_prompt(agent_id=1, question=message)
"""

import os
import json
import requests
from typing import List
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────

PLEIADE_BASE_URL   = "https://pleiade.mi.parisdescartes.fr"
TOKEN_PLEIADE      = os.getenv("TOKEN_PLEIADE", "")
EMBEDDING_MODEL    = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
CHROMA_DIR         = os.getenv("CHROMA_DIR", "chroma_db")
CHUNK_SIZE         = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP      = int(os.getenv("CHUNK_OVERLAP", "50"))

# Nom de la collection ChromaDB — une collection unique, les docs sont filtrés par metadata
CHROMA_COLLECTION  = "ai_taskforce_rag"


class RAGService:
    """
    Service RAG : indexation et recherche de documents via embeddings.

    Une seule instance ChromaDB est utilisée (singleton paresseux).
    Les documents sont isolés par agent_id dans les métadonnées.
    """

    def __init__(self):
        self._collection = None   # chargé à la demande (lazy)

    # ──────────────────────────────────────────────────────────────────────────
    # PROPRIÉTÉ : collection ChromaDB (singleton paresseux)
    # ──────────────────────────────────────────────────────────────────────────

    @property
    def collection(self):
        """
        Initialise ChromaDB et retourne la collection au premier appel.
        Évite d'importer chromadb au démarrage si le service n'est pas utilisé.
        """
        if self._collection is None:
            import chromadb
            client = chromadb.PersistentClient(path=CHROMA_DIR)
            self._collection = client.get_or_create_collection(
                name=CHROMA_COLLECTION,
                # Cosine similarity — meilleure distance pour les embeddings texte
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    # ──────────────────────────────────────────────────────────────────────────
    # ÉTAPE 1 : EXTRACTION DU TEXTE
    # ──────────────────────────────────────────────────────────────────────────

    def _extraire_texte(self, chemin: str) -> str:
        """
        Extrait le texte brut d'un fichier selon son extension.

        Formats supportés : .txt, .md, .pdf, .docx

        Args:
            chemin (str): Chemin absolu vers le fichier.

        Returns:
            str: Contenu textuel extrait.

        Raises:
            ValueError: Si le format n'est pas supporté.
            FileNotFoundError: Si le fichier n'existe pas.
        """
        if not os.path.exists(chemin):
            raise FileNotFoundError(f"Fichier introuvable : {chemin}")

        ext = os.path.splitext(chemin)[1].lower()

        if ext in (".txt", ".md"):
            with open(chemin, "r", encoding="utf-8") as f:
                return f.read()

        elif ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(chemin)
            return "\n".join(page.extract_text() or "" for page in reader.pages)

        elif ext == ".docx":
            # python-docx
            from docx import Document as DocxDocument
            doc = DocxDocument(chemin)
            return "\n".join(p.text for p in doc.paragraphs)

        else:
            raise ValueError(f"Format non supporté pour le RAG : {ext}")

    # ──────────────────────────────────────────────────────────────────────────
    # ÉTAPE 2 : DÉCOUPAGE EN CHUNKS
    # ──────────────────────────────────────────────────────────────────────────

    def _decouper_en_chunks(self, texte: str) -> List[str]:
        """
        Découpe le texte en segments de taille CHUNK_SIZE mots
        avec un chevauchement de CHUNK_OVERLAP mots.

        Le chevauchement (overlap) garantit que les informations
        à la frontière entre deux chunks ne sont pas perdues.

        Exemple avec CHUNK_SIZE=5, CHUNK_OVERLAP=2 :
          Texte : "A B C D E F G H"
          Chunks: ["A B C D E", "D E F G H"]

        Args:
            texte (str): Texte brut à découper.

        Returns:
            List[str]: Liste de chunks non vides.
        """
        mots = texte.split()
        chunks = []
        i = 0
        while i < len(mots):
            chunk = " ".join(mots[i: i + CHUNK_SIZE])
            if chunk.strip():
                chunks.append(chunk)
            i += CHUNK_SIZE - CHUNK_OVERLAP  # avancer en tenant compte du overlap
        return chunks

    # ──────────────────────────────────────────────────────────────────────────
    # ÉTAPE 3 : GÉNÉRATION DES EMBEDDINGS VIA PLÉIADE
    # ──────────────────────────────────────────────────────────────────────────

    def _generer_embedding(self, texte: str) -> List[float]:
        """
        Génère un vecteur d'embedding pour un texte via l'API Pléiade.

        L'endpoint utilisé est compatible OpenAI :
          POST /api/embeddings
          Body : {"model": "nomic-embed-text:latest", "input": "..."}

        Args:
            texte (str): Texte à vectoriser.

        Returns:
            List[float]: Vecteur d'embedding (dimension dépend du modèle).

        Raises:
            RuntimeError: Si l'API Pléiade retourne une erreur.
        """
        headers = {
            "Authorization": f"Bearer {TOKEN_PLEIADE}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": EMBEDDING_MODEL,
            "input": texte,
        }

        response = requests.post(
            f"{PLEIADE_BASE_URL}/api/embeddings",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Erreur Pléiade embeddings {response.status_code} : {response.text}"
            )

        data = response.json()
        # Format OpenAI : {"data": [{"embedding": [...]}]}
        return data["data"][0]["embedding"]

    def _generer_embeddings_batch(self, textes: List[str]) -> List[List[float]]:
        """
        Génère les embeddings pour une liste de textes.
        Appels séquentiels (Pléiade ne supporte pas le batch natif).

        Args:
            textes (List[str]): Liste de textes.

        Returns:
            List[List[float]]: Liste de vecteurs dans le même ordre.
        """
        return [self._generer_embedding(t) for t in textes]

    # ──────────────────────────────────────────────────────────────────────────
    # ÉTAPE 4 : INDEXATION COMPLÈTE D'UN DOCUMENT
    # ──────────────────────────────────────────────────────────────────────────

    def indexer_document(self, doc_id: int, agent_id: int, chemin_fichier: str) -> int:
        """
        Pipeline complet : lecture → découpage → embeddings → stockage ChromaDB.

        Appelé par DocumentService.sauvegarder() après l'upload.

        Args:
            doc_id        (int): ID du document en base (clé étrangère).
            agent_id      (int): ID de l'agent propriétaire.
            chemin_fichier(str): Chemin absolu vers le fichier.

        Returns:
            int: Nombre de chunks indexés.

        Raises:
            FileNotFoundError: Si le fichier est introuvable.
            RuntimeError: Si l'API Pléiade échoue.
        """
        print(f"[RAGService] Indexation doc_id={doc_id}, agent_id={agent_id}...")

        # 1. Extraction
        texte = self._extraire_texte(chemin_fichier)
        if not texte.strip():
            print(f"[RAGService] ⚠ Document vide, aucun chunk indexé.")
            return 0

        # 2. Découpage
        chunks = self._decouper_en_chunks(texte)
        print(f"[RAGService] {len(chunks)} chunks générés.")

        # 3. Embeddings
        embeddings = self._generer_embeddings_batch(chunks)

        # 4. Stockage ChromaDB
        # IDs uniques : "doc_{doc_id}_chunk_{i}"
        ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]

        # Métadonnées stockées avec chaque chunk pour filtrer lors de la recherche
        metadatas = [
            {
                "doc_id": doc_id,
                "agent_id": agent_id,
                "chunk_index": i,
                "chemin": chemin_fichier,
            }
            for i in range(len(chunks))
        ]

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(f"[RAGService] ✅ {len(chunks)} chunks indexés dans ChromaDB.")
        return len(chunks)

    # ──────────────────────────────────────────────────────────────────────────
    # RECHERCHE
    # ──────────────────────────────────────────────────────────────────────────

    def rechercher(self, agent_id: int, question: str, top_k: int = 5) -> List[str]:
        """
        Recherche les chunks les plus pertinents pour une question.

        Filtre automatiquement par agent_id pour que chaque agent
        ne voit que ses propres documents.

        Args:
            agent_id (int): ID de l'agent (filtre de sécurité).
            question (str): Question ou prompt de l'utilisateur.
            top_k    (int): Nombre de chunks à retourner (défaut: 5).

        Returns:
            List[str]: Liste des chunks les plus pertinents, du plus au moins pertinent.
        """
        if not question.strip():
            return []

        # Vectoriser la question
        embedding_question = self._generer_embedding(question)

        # Recherche dans ChromaDB — filtrer par agent_id
        resultats = self.collection.query(
            query_embeddings=[embedding_question],
            n_results=top_k,
            where={"agent_id": agent_id},        # filtre sur les métadonnées
            include=["documents", "distances"],
        )

        # resultats["documents"] est une liste de listes [[chunk1, chunk2, ...]]
        chunks = resultats.get("documents", [[]])[0]
        return chunks

    # ──────────────────────────────────────────────────────────────────────────
    # CONTEXTE POUR PROMPT (intégration dans Agent)
    # ──────────────────────────────────────────────────────────────────────────

    def contexte_pour_prompt(self, agent_id: int, question: str, top_k: int = 5) -> str:
        """
        Retourne les chunks pertinents formatés comme contexte pour le LLM.

        Usage typique dans Agent.executer_prompt() :
          contexte = rag.contexte_pour_prompt(self.ID, message)
          prompt_enrichi = contexte + "\\n\\nQuestion : " + message

        Args:
            agent_id (int): ID de l'agent.
            question (str): Question de l'utilisateur.
            top_k    (int): Nombre de chunks à inclure.

        Returns:
            str: Texte formaté à injecter dans le prompt, ou "" si aucun résultat.
        """
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

    def supprimer_document(self, doc_id: int) -> None:
        """
        Supprime tous les chunks d'un document de ChromaDB.

        Appelé par DocumentService.supprimer() avant la suppression en base.

        Args:
            doc_id (int): ID du document dont les vecteurs doivent être supprimés.
        """
        self.collection.delete(where={"doc_id": doc_id})
        print(f"[RAGService] Vecteurs du doc_id={doc_id} supprimés de ChromaDB.")

    def supprimer_agent(self, agent_id: int) -> None:
        """
        Supprime tous les vecteurs de tous les documents d'un agent.

        Appelé lors de la suppression complète d'un agent.

        Args:
            agent_id (int): ID de l'agent.
        """
        self.collection.delete(where={"agent_id": agent_id})
        print(f"[RAGService] Tous les vecteurs de agent_id={agent_id} supprimés.")
