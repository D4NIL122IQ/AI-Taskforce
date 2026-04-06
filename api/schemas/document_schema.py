from pydantic import BaseModel, ConfigDict
from datetime import datetime


class DocumentResponse(BaseModel):
    """
    Schéma de réponse pour un document.
    Utilisé pour sérialiser un objet Document SQLAlchemy en JSON.
    """
    id_document: int
    nom_fichier: str        # Nom original du fichier (ex: "rapport.pdf")
    type_fichier: str       # Extension sans point (ex: "pdf", "txt")
    chemin: str             # Chemin physique sur le disque
    date_upload: datetime   # Date d'upload (UTC)
    agent_id: int           # ID de l'agent propriétaire

    # Permet à Pydantic de lire les attributs SQLAlchemy directement
    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    """
    Réponse retournée après un upload réussi.
    Contient un message de confirmation et le document créé.
    """
    message: str                  # Ex: "Document indexé avec succès"
    document: DocumentResponse    # Le document créé avec son id_document