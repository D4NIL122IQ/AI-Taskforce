from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.appDatabase.database import get_db
from api.schemas.workflow_schema import WorkflowCreate, WorkflowUpdate, WorkflowResponse
from backend.services import workflow_service

router = APIRouter(prefix="/workflows", tags=["Workflows"])



@router.get("/user/{user_id}", response_model=list[WorkflowResponse])
def list_workflows(user_id: int, db: Session = Depends(get_db)):
    return workflow_service.get_all_workflows(db, user_id)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = workflow_service.get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow non trouvé")
    return workflow


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(data: WorkflowCreate, db: Session = Depends(get_db)):
    return workflow_service.create_workflow(db, data)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(workflow_id: int, data: WorkflowUpdate, db: Session = Depends(get_db)):
    workflow = workflow_service.update_workflow(db, workflow_id, data)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow non trouvé")
    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    if not workflow_service.delete_workflow(db, workflow_id):
        raise HTTPException(status_code=404, detail="Workflow non trouvé")
