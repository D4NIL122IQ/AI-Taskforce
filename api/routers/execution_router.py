from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json

from backend.appDatabase.database import get_db
from backend.models.execution_model import Execution
from backend.modeles.Agent import Agent as AgentLLM
from backend.modeles.orchestration import Orchestration

router = APIRouter(prefix="/executions", tags=["Executions"])


# ── Schéma de la requête /execute ─────────────────────────────────────────────

class NodeData(BaseModel):
    label: str = "Agent"
    role: str = ""
    model: str = "Pleiade"
    system_prompt: str = ""
    max_tokens: int = 800
    temperature: float = 0.3

class WorkflowNode(BaseModel):
    id: str
    type: str
    data: NodeData

class ExecuteRequest(BaseModel):
    prompt: str
    nodes: list[WorkflowNode]
    niveau_recherche: int = 1
    workflow_id: int | None = None


# ── Endpoint principal ─────────────────────────────────────────────────────────



@router.post("/execute")
def execute_workflow(body: ExecuteRequest, db: Session = Depends(get_db)):
    supervisor_node = next((n for n in body.nodes if n.type == "supervisor"), None)
    agent_nodes     = [n for n in body.nodes if n.type == "agent"]

    if not supervisor_node:
        raise HTTPException(status_code=400, detail="Aucun nœud superviseur trouvé.")
    if len(agent_nodes) < 1:
        raise HTTPException(status_code=400, detail="Au moins 1 agent spécialiste requis.")

    noms_agents = ", ".join(n.data.label for n in agent_nodes)
    prompt_superviseur = (
        f"Tu es un superviseur qui coordonne : {noms_agents}.\n"
        "Délègue chaque sous-tâche à l'agent le plus adapté selon son rôle.\n"
        "Une fois tous les agents consultés, route vers 'reconstructeur'.\n"
        "Réponds UNIQUEMENT en JSON valide :\n"
        '{"next_agent": "nom_du_specialiste", "prompt": "instructions"}\n'
        'Ou si terminé : {"next_agent": "reconstructeur", "prompt": ""}'
    )
    if supervisor_node.data.system_prompt.strip():
        prompt_superviseur = supervisor_node.data.system_prompt

    try:
        superviseur = AgentLLM(
            nom="superviseur",
            modele=_normalise_modele(supervisor_node.data.model),
            prompt=prompt_superviseur,
            max_token=min(supervisor_node.data.max_tokens, 8192),
            temperature=_clamp(supervisor_node.data.temperature),
        )
        specialistes = []
        for n in agent_nodes:
            prompt_agent = n.data.system_prompt.strip() or (
                f"Tu es {n.data.label}, un expert en : {n.data.role or n.data.label}. "
                "Réponds de façon précise et structurée."
            )
            specialistes.append(AgentLLM(
                nom=n.data.label,
                modele=_normalise_modele(n.data.model),
                prompt=prompt_agent,
                max_token=min(n.data.max_tokens, 8192),
                temperature=_clamp(n.data.temperature),
            ))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Configuration agent invalide : {e}")

    def generate():
        try:
            niveau = body.niveau_recherche if body.niveau_recherche in (1, 2, 3) else 1
            orche = Orchestration(superviseur=superviseur, specialistes=specialistes, niveau_recherche=niveau)
            final_state = orche.executer(body.prompt)

            reponse = final_state.get("final_response", "")
            echanges = final_state.get("results", {})

    # Sauvegarde en base (optionnel, ne bloque pas si échec)
    try:
        execution = Execution(
            workflow_id=body.workflow_id,
            status="TERMINE",
            prompt=body.prompt,
            outputs_json={"final_response": reponse}
        )

        db.add(execution)
        db.commit()
        db.refresh(execution)

        print("execution sauvegardée")

    except Exception as e:
        db.rollback() 
        print("Erreur sauvegarde :", e)

            # Envoie la réponse finale
            yield json.dumps({
                "type": "final",
                "response": reponse
            }) + "\n"

        except Exception as e:
            yield json.dumps({
                "type": "error",
                "message": str(e)
            }) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
# ── CRUD existant ──────────────────────────────────────────────────────────────

@router.get("/")
def get_all_executions(db: Session = Depends(get_db)):
    return [_fmt(e) for e in db.query(Execution).order_by(Execution.date_execution.desc()).all()]

@router.get("/{status}")
def get_executions(status: str, db: Session = Depends(get_db)):
    return [_fmt(e) for e in db.query(Execution).filter(Execution.status == status).all()]

@router.post("/")
def create_execution(workflow_id: int, db: Session = Depends(get_db)):
    e = Execution(workflow_id=workflow_id, status="EN_COURS")
    db.add(e); db.commit(); db.refresh(e)
    return {"id_execution": e.id_execution, "status": e.status}

@router.delete("/{execution_id}")
def delete_execution(execution_id: int, db: Session = Depends(get_db)):
    e = db.query(Execution).filter(Execution.id_execution == execution_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Exécution non trouvée")
    db.delete(e); db.commit()
    return {"message": f"Exécution {execution_id} supprimée"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _fmt(e):
    return {
        "id": e.id_execution,
        "workflow_id": e.workflow_id,
        "status": e.status,
        "date_execution": e.date_execution.isoformat() if e.date_execution else None,
        "history": e.history_json or {},
        "outputs": e.outputs_json or {},
    }

def _normalise_modele(model_str: str) -> str:
    mapping = {"pleiade": "Pleiade", "mistral": "Mistral", "openai": "Openai",
               "anthropic": "Anthropic", "gemini": "Gemini", "ollama": "Ollama", "deepseek": "DeepSeek"}
    return mapping.get(model_str.lower(), "Pleiade")

def _clamp(val: float) -> float:
    return max(0.0, min(1.0, float(val)))