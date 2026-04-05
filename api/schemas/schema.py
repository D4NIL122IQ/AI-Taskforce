from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class WorkflowCreate(BaseModel):
    nom: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    superviseur_id: Optional[int] = None
    utilisateur_id: Optional[int] = None

class AgentData(BaseModel):
    nom:str
    modele:str
    prompt:str
    max_token:int
    temperature:int
    user_id:int

class UserData(BaseModel):
    user_id: Optional[int] = None
    nom:str
    email:str
    mot_de_passe:str

class execitionData(BaseModel):
    execution_id: int
    workfliow_id:int
    prompt:str
    status:str
    date_execution: Optional[str] = None

class DocumentData(BaseModel):
    id_document: Optional[int] = None
    nom: str
    path: str
    type: str
    id_agent: int
