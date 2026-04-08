from fastapi import APIRouter, Depends,HTTPException
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

@router.post("/")
def create_execution(workflow_id: int, db: Session = Depends(get_db)):
    execution = Execution(workflow_id=workflow_id, status="EN_COURS")
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return {"id_execution": execution.id_execution, "status": execution.status}


@router.delete("/{execution_id}")
def delete_execution(execution_id: int, db: Session = Depends(get_db)):
    execution = db.query(Execution).filter(Execution.id_execution == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Exécution non trouvée")
    db.delete(execution)
    db.commit()
    return {"message": f"Exécution {execution_id} supprimée"}