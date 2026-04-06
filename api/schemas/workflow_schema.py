from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime


class WorkflowBase(BaseModel):
    nom: str
    donnees_graphe_json: Optional[Any] = None
    superviseur_id: Optional[int] = None


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(WorkflowBase):
    pass


class WorkflowResponse(WorkflowBase):
    id_workflow: int
    date_creation: datetime | None = None
    utilisateur_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
