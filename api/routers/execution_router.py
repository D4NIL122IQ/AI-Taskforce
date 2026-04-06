from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.appDatabase.database import get_db
from backend.models.execution_model import Execution
from api.schemas.execution_schema import ExecutionData

router = APIRouter(prefix="/executions", tags=["Executions"])

@router.get("/")
def get_all_executions(db: Session = Depends(get_db)):
    executions = db.query(Execution).all()

    return [
        {
            "id": e.id_execution,
            "workflow_id": e.workflow_id,
            "status": e.status,
            "date_execution": e.date_execution.isoformat() if e.date_execution else None,
            "history": e.history_json or {},
            "outputs": e.outputs_json or {}
        }
        for e in executions
    ]

@router.get("/{status}")
def get_executions(status: str, db: Session = Depends(get_db)):
    executions = db.query(Execution).filter(Execution.status == status).all()

    return [
        {
            "id": e.id_execution,
            "workflow_id": e.workflow_id,
            "status": e.status,
            "date_execution": e.date_execution.isoformat() if e.date_execution else None,
            "history": e.history_json or {},
            "outputs": e.outputs_json or {}
        }

        for e in executions
    ]