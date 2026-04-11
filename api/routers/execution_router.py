from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json

from backend.appDatabase.database import get_db, SessionLocal
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
    web_search: bool = False

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
                use_web=n.data.web_search,
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

            # Envoie les échanges agent par agent
            for agent_nom, agent_reponse in echanges.items():
                yield json.dumps({
                    "type": "echange",
                    "agent": agent_nom,
                    "content": agent_reponse
                }) + "\n"

            # Après le yield des échanges
            supervisor_logs = final_state.get("supervisor_logs", [])
            for log in supervisor_logs:
                yield json.dumps({
                    "type": "supervisor",
                    "content": log
                }) + "\n"

            # Envoie la réponse finale
            yield json.dumps({
                "type": "final",
                "response": reponse
            }) + "\n"

            # Sauvegarde en base
            try:
                db_save = SessionLocal()
                execution = Execution(
                    workflow_id=body.workflow_id,
                    status="TERMINE",
                    outputs_json={"final_response": reponse}
                )
                db_save.add(execution)
                db_save.commit()
                db_save.close()
                print("Execution sauvegardée")
            except Exception as e:
                print("Erreur sauvegarde :", e)

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
    # Si c'est un nom de modèle réel (ex: "phi4:latest", "athene-v2:latest") → passer tel quel
    if ":" in model_str or "." in model_str:
        return model_str
    # Sinon c'est un nom de provider → mapper vers le modèle par défaut
    mapping = {
        "pleiade": "phi4:latest",
        "ollama": "llama3.2",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-haiku-4-5-20251001",
        "gemini": "gemini-1.5-flash",
        "mistral": "mistral-small-latest",
        "deepseek": "deepseek-chat",
    }
    return mapping.get(model_str.lower(), "phi4:latest")

def _clamp(val: float) -> float:
    return max(0.0, min(1.0, float(val)))