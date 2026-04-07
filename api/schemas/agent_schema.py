from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class AgentBase(BaseModel):
    nom: str
    role: Optional[str] = None
    modele: str
    temperature: float = 0.7
    max_tokens: int = 1024
    system_prompt: Optional[str] = None
    statut: str = "ACTIF"
    utilisateur_id: Optional[int] = None


class AgentCreate(AgentBase):
    pass


class AgentUpdate(AgentBase):
    pass


class AgentResponse(AgentBase):
    id_agent: int
    date_creation: datetime
    utilisateur_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
