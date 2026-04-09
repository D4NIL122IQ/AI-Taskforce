from sqlalchemy.orm import Session
from backend.models.workflow_model import Workflow
from api.schemas.workflow_schema import WorkflowCreate, WorkflowUpdate


def get_all_workflows(db: Session, user_id: int) -> list[Workflow]:
    return db.query(Workflow).filter(Workflow.utilisateur_id == user_id).all()


def get_workflow_by_id(db: Session, workflow_id: str) -> Workflow | None:
    return db.query(Workflow).filter(Workflow.id_workflow == workflow_id).first()


def create_workflow(db: Session, data: WorkflowCreate) -> Workflow:
    workflow = Workflow(
        nom=data.nom,
        donnees_graphe_json=data.donnees_graphe_json,
        superviseur_id=data.superviseur_id,
        utilisateur_id=data.utilisateur_id,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def update_workflow(db: Session, workflow_id: int, data: WorkflowUpdate) -> Workflow | None:
    workflow = get_workflow_by_id(db, workflow_id)
    if not workflow:
        return None
    for field, value in data.model_dump().items():
        setattr(workflow, field, value)
    db.commit()
    db.refresh(workflow)
    return workflow


def delete_workflow(db: Session, workflow_id: int) -> bool:
    workflow = get_workflow_by_id(db, workflow_id)
    if not workflow:
        return False
    db.delete(workflow)
    db.commit()
    return True
