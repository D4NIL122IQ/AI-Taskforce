from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime
import uuid
from typing import Optional, Any


class WorkflowBase(BaseModel):
    nom: str
    donnees_graphe_json: Optional[Any] = None
    superviseur_id: Optional[int] = None


class WorkflowCreate(WorkflowBase):
    utilisateur_id: Optional[uuid.UUID] = None


class WorkflowUpdate(WorkflowBase):
    pass


class WorkflowResponse(WorkflowBase):
    id_workflow: int
    date_creation: Optional[datetime] = None
    utilisateur_id: Optional[uuid.UUID] = None
