from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel

class UserData(BaseModel):
    nom: str
    email: str
    mot_de_passe: str

class UserLogin(BaseModel):
    email: str
    mot_de_passe: str