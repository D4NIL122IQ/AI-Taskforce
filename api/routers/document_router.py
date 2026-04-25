# api/routers/document_router.py
"""
DocumentRouter — Endpoints pour la gestion des documents RAG.

ENDPOINTS :
  POST   /agents/{agent_id}/documents        → Upload et indexation d'un document
  GET    /agents/{agent_id}/documents        → Lister les documents d'un agent
  DELETE /documents/{doc_id}                 → Supprimer un document
  GET    /agents/{agent_id}/rag-config       → Lire la config RAG d'un agent
  POST   /agents/{agent_id}/rag-config       → Sauvegarder la config RAG d'un agent
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
import json
from pathlib import Path

from backend.appDatabase.database import get_db
from backend.services.document_service import DocumentService
from backend.services.rag_service import RAGService
from api.schemas.document_schema import DocumentResponse, DocumentUploadResponse

# ── Config RAG persistée par agent (fichier JSON) ─────────────────────────────
RAG_CONFIG_DIR = Path("rag_configs")
RAG_CONFIG_DIR.mkdir(exist_ok=True)

RAG_CONFIG_DEFAULTS = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "top_k": 5,
    "lambda_mult": 0.5,
    "use_post_processing": True,
}

class RagConfig(BaseModel):
    chunk_size: int       = Field(default=500,  ge=100,  le=2000)
    chunk_overlap: int    = Field(default=50,   ge=0,    le=500)
    top_k: int            = Field(default=5,    ge=1,    le=30)
    lambda_mult: float    = Field(default=0.5,  ge=0.0,  le=1.0)
    use_post_processing: bool = False

def _config_path(agent_id: int) -> Path:
    return RAG_CONFIG_DIR / f"agent_{agent_id}.json"

def _load_config(agent_id: int) -> dict:
    path = _config_path(agent_id)
    if path.exists():
        return json.loads(path.read_text())
    return RAG_CONFIG_DEFAULTS.copy()

router = APIRouter(prefix="/agents", tags=["documents"])


@router.post("/{agent_id}/documents", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    agent_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload un fichier et l'indexe dans ChromaDB pour le RAG.
    Formats acceptés : .pdf, .txt, .docx, .md
    """
    # Lire les bytes du fichier uploadé
    file_bytes = await file.read()

    # Sauvegarder en base + sur le disque
    svc = DocumentService(db)
    try:
        doc = svc.sauvegarder(
            agent_id=agent_id,
            filename=file.filename,
            file_bytes=file_bytes
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Indexer dans ChromaDB
    try: 
        print((f"[Agent {agent_id}] Lancement de l'indexation RAG  {doc.id_document} "))
        background_tasks.add_task(
            RAGService().indexer_document,
            doc_id=doc.id_document,
            agent_id=agent_id,
            chemin_fichier=doc.chemin)
        
    except Exception as e:
        # Ne pas bloquer si ChromaDB échoue
        print(f"[DocumentRouter] Indexation RAG échouée : {e}")

    return DocumentUploadResponse(
        message=f"Document '{doc.nom_fichier}' uploadé et indexé avec succès.",
        document=doc
    )


@router.get("/{agent_id}/documents", response_model=List[DocumentResponse])
def lister_documents(agent_id: int, db: Session = Depends(get_db)):
    """
    Retourne tous les documents associés à un agent.
    """
    svc = DocumentService(db)
    return svc.lister(agent_id=agent_id)


@router.delete("/documents/{doc_id}")
def supprimer_document(doc_id: int, db: Session = Depends(get_db)):
    """
    Supprime un document : fichier physique + vecteurs ChromaDB + entrée BDD.
    """
    svc = DocumentService(db)
    supprime = svc.supprimer(doc_id=doc_id)
    if not supprime:
        raise HTTPException(status_code=404, detail="Document introuvable.")
    return {"message": f"Document {doc_id} supprimé avec succès."}

@router.get("/user/{user_id}/documents", response_model=List[DocumentResponse])
def lister_documents_utilisateur(user_id: str, db: Session = Depends(get_db)):
    """
    Retourne tous les documents de tous les agents d'un utilisateur.
    """
    from backend.models.agent_model import Agent
    agents = db.query(Agent).filter(Agent.utilisateur_id == user_id).all()
    tous_les_docs = []
    for agent in agents:
        svc = DocumentService(db)
        docs = svc.lister(agent_id=agent.id_agent)
        tous_les_docs.extend(docs)
    return tous_les_docs


# ------- Endpoints config RAG ---------------------------

@router.get("/{agent_id}/rag-config")
def get_rag_config(agent_id: int):
    """Retourne la config RAG de l'agent (défauts si jamais configuré)."""
    return _load_config(agent_id)


@router.post("/{agent_id}/rag-config")
def save_rag_config(agent_id: int, config: RagConfig):
    """Sauvegarde la config RAG de l'agent."""
    _config_path(agent_id).write_text(json.dumps(config.model_dump(), indent=2))
    return {"message": "Configuration RAG sauvegardée.", "config": config.model_dump()}