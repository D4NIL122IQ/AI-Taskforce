from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.appDatabase.database import get_db
from backend.models.workflow_model import Workflow
from api.schemas.schema import WorkflowCreate

router = APIRouter(prefix="/workflows", tags=["Workflows"])


# tous les workflows
@router.get("/{user_id}")
def get_workflows(user_id: int, db: Session = Depends(get_db)):
    workflows = db.query(Workflow).filter(Workflow.utilisateur_id == user_id).all()

    result = []
    for w in workflows:
        nb_agents = 0

        if w.donnees_graphe_json:
            nb_agents = len(w.donnees_graphe_json.get("nodes", []))

        result.append({
            "id": w.id_workflow,
            "nom": w.nom,
            "nb_agents": nb_agents,
            "date": w.date_creation
        })

    return result


# POST créer un workflow
@router.post("/")
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):

    new_workflow = Workflow(
        nom=workflow.nom,
        donnees_graphe_json={
            "nodes": workflow.nodes,
            "edges": workflow.edges
        },
        superviseur_id=workflow.superviseur_id,
        utilisateur_id=workflow.utilisateur_id
    )

    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)

    return {
        "message": "Workflow créé avec succès",
        "id": new_workflow.id_workflow
    }