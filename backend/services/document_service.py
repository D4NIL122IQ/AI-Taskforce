# backend/services/document_service.py
"""
DocumentService — Couche service pour la gestion des documents.

RESPONSABILITÉS :
  1. Sauvegarder le fichier physique sur le disque (dossier uploads/)
  2. Créer / lire / supprimer l'entrée dans la table `document` (SQLAlchemy)
  3. Lister les documents d'un agent
  4. NE PAS toucher aux embeddings → c'est le rôle de RAGService

DÉPENDANCES :
  - backend/models/document_model.py  → classe Document (SQLAlchemy)
  - backend/appDatabase/database.py   → get_db() (session SQLAlchemy)
  - backend/services/rag_service.py   → appelé par delete() pour nettoyer ChromaDB

UTILISATION :
  from backend.services.document_service import DocumentService

  svc = DocumentService(db_session)
  doc = svc.sauvegarder(agent_id=1, filename="rapport.pdf", file_bytes=b"...")
  docs = svc.lister(agent_id=1)
  svc.supprimer(doc_id=42)
"""

import os
import uuid
from typing import List

from sqlalchemy.orm import Session

from backend.models.document_model import Document
from backend.services.rag_service import RAGService
from backend.services.rag_service import RAGService


# ── Dossier de stockage des fichiers uploadés ─────────────────────────────────
# Modifiable via variable d'environnement UPLOAD_DIR (ex: volume Docker)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

# Extensions acceptées (cohérent avec ajouter_document() dans Agent.py)
EXTENSIONS_AUTORISEES = {".pdf", ".txt", ".docx", ".md"}


class DocumentService:
    """
    Service de gestion du cycle de vie des documents.

    Chaque méthode reçoit une session SQLAlchemy en dépendance
    pour rester compatible avec FastAPI (Depends(get_db)).
    """

    def __init__(self, db: Session):
        self.db = db
        # Crée le dossier uploads/ s'il n'existe pas
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    # ──────────────────────────────────────────────────────────────────────────
    # SAUVEGARDER
    # ──────────────────────────────────────────────────────────────────────────

    def sauvegarder(self, agent_id: int, filename: str, file_bytes: bytes) -> Document:
        """
        Sauvegarde un fichier sur le disque et crée son entrée en base.

        Le nom de fichier sur le disque est rendu unique via un UUID
        pour éviter les collisions (ex: deux agents uploadent "rapport.pdf").

        Args:
            agent_id  (int):   ID de l'agent propriétaire du document.
            filename  (str):   Nom original du fichier (ex: "rapport.pdf").
            file_bytes(bytes): Contenu binaire du fichier.

        Returns:
            Document: L'objet SQLAlchemy inséré en base (avec son id_document).

        Raises:
            ValueError: Si l'extension du fichier n'est pas supportée.
            ValueError: Si file_bytes est vide.
        """
        if not file_bytes:
            raise ValueError("Le fichier est vide.")

        extension = os.path.splitext(filename)[1].lower()
        if extension not in EXTENSIONS_AUTORISEES:
            raise ValueError(
                f"Extension '{extension}' non supportée. "
                f"Extensions acceptées : {EXTENSIONS_AUTORISEES}"
            )
        
        # Vérifie l'unicité  de fichier pour agent
        docs = self.db.query(Document).filter(Document.agent_id == agent_id).all()
        for doc in docs:
            if doc.nom_fichier == filename:
                raise ValueError(f"Un document nommé '{filename}' existe déjà pour cet agent.") 

        # Nom unique sur le disque : uuid + extension d'origine
        nom_unique = f"{uuid.uuid4().hex}{extension}"
        chemin_absolu = os.path.join(UPLOAD_DIR, nom_unique)

        # Écriture physique
        with open(chemin_absolu, "wb") as f:
            f.write(file_bytes)

        # Entrée en base
        doc = Document(
            nom_fichier=filename,
            type_fichier=extension.lstrip("."),   # "pdf", "txt"…
            chemin=chemin_absolu,
            agent_id=agent_id,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)

        return doc

    # ──────────────────────────────────────────────────────────────────────────
    # LISTER
    # ──────────────────────────────────────────────────────────────────────────

    def lister(self, agent_id: int) -> List[Document]:
        """
        Retourne tous les documents associés à un agent.

        Args:
            agent_id (int): ID de l'agent.

        Returns:
            List[Document]: Liste (possiblement vide) des documents.
        """
        return (
            self.db.query(Document)
            .filter(Document.agent_id == agent_id)
            .order_by(Document.date_upload)
            .all()
        )

    # ──────────────────────────────────────────────────────────────────────────
    # OBTENIR PAR ID
    # ──────────────────────────────────────────────────────────────────────────

    def obtenir(self, doc_id: int) -> Document:
        """
        Retourne un document par son ID.

        Args:
            doc_id (int): ID du document.

        Returns:
            Document | None: Le document ou None s'il n'existe pas.
        """
        return self.db.query(Document).filter(Document.id_document == doc_id).first()

    # ──────────────────────────────────────────────────────────────────────────
    # SUPPRIMER
    # ──────────────────────────────────────────────────────────────────────────

    def supprimer(self, doc_id: int) -> bool:
        """
        Supprime un document :
          1. Supprime le fichier physique du disque.
          2. Supprime les vecteurs dans ChromaDB (via RAGService).
          3. Supprime l'entrée en base.

        Args:
            doc_id (int): ID du document à supprimer.

        Returns:
            bool: True si supprimé, False si document introuvable.
        """
        doc = self.obtenir(doc_id)
        if doc is None:
            return False

        # 1. Fichier physique
        if os.path.exists(doc.chemin):
            os.remove(doc.chemin)

        # 2. Vecteurs ChromaDB (import local pour éviter la circularité)
        try:
            from backend.services.rag_service import RAGService
            RAGService().supprimer_document(doc_id)
        except Exception as e:
            # Ne pas bloquer la suppression si ChromaDB échoue
            print(f"[DocumentService] ⚠ Impossible de supprimer les vecteurs : {e}")

        # 3. Base de données
        self.db.delete(doc)
        self.db.commit()

        return True