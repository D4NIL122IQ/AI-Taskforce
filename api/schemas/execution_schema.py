from typing import Optional
from pydantic import BaseModel

class ExecutionData(BaseModel):
    execution_id: int
    workflow_id: int
    prompt: str
    status: str
    date_execution: Optional[str] = None