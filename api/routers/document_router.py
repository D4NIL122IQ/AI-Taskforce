# api/routers/document_router.py
"""
DocumentRouter — Endpoints pour la gestion des documents RAG.

ENDPOINTS :
  POST   /agents/{agent_id}/documents        → Upload et indexation d'un document
  GET    /agents/{agent_id}/documents        → Lister les documents d'un agent
  DELETE /documents/{doc_id}                 → Supprimer un document
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from backend.appDatabase.database import get_db
from backend.services.document_service import DocumentService
from backend.services.rag_service import RAGService
from api.schemas.document_schema import DocumentResponse, DocumentUploadResponse

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
        background_tasks.add_task(
            RAGService().indexer_document,
            doc_id=doc.id_document,
            agent_id=agent_id,
            chemin_fichier=doc.chemin)
        
    except Exception as e:
        # Ne pas bloquer si ChromaDB échoue
        print(f"[DocumentRouter] ⚠ Indexation RAG échouée : {e}")

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