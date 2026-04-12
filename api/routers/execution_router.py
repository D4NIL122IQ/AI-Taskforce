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

from backend.services.mcp_token_service import (
    McpTokenService,
    McpTokenNotFoundError,
    McpTokenExpiredError,
)

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
    utilise_mcp: bool = False   # L'agent doit-il se connecter à un MCP ?
    mcp_type: str = ""          # "github" | "gmail" — ignoré si utilise_mcp=False

class WorkflowNode(BaseModel):
    id: str
    type: str
    data: NodeData

class ExecuteRequest(BaseModel):
    prompt: str
    nodes: list[WorkflowNode]
    niveau_recherche: int = 1
    workflow_id: int | None = None

class McpTokenCreate(BaseModel):
    mcp_type: str        # "github" | "gmail"
    token_public: str    # client_id OAuth
    access_token: str
    refresh_token: str


# ── Endpoint principal ─────────────────────────────────────────────────────────

@router.post("/execute")
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
 
            agent = AgentLLM(
                nom=n.data.label,
                modele=_normalise_modele(n.data.model),
                prompt=prompt_agent,
                max_token=min(n.data.max_tokens, 8192),
                temperature=_clamp(n.data.temperature),
                use_web=n.data.web_search,
                utilise_mcp=n.data.utilise_mcp,
            )
 
            # ── Connexion MCP si demandée ─────────────────────────────────────
            # McpTokenService lit les tokens en BDD et appelle agent.connecter_mcp().
            # Si l'access_token est expiré (401), il rafraîchit automatiquement
            # via OAuth et met à jour la BDD avant de reconnecter l'agent.
            if n.data.utilise_mcp and n.data.mcp_type:
                if body.workflow_id is None:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"L'agent '{n.data.label}' utilise MCP mais "
                            "workflow_id est absent de la requête."
                        ),
                    )
                try:
                    McpTokenService(db).connecter_agent_mcp(
                        agent=agent,
                        workflow_id=body.workflow_id,
                        mcp_type=n.data.mcp_type,
                    )
                except McpTokenNotFoundError as e:
                    # Pas de token en BDD → on log et on continue sans MCP
                    # (l'agent fonctionnera normalement, juste sans les outils MCP)
                    print(f"[execution_router] ⚠ {e}")
                except McpTokenExpiredError as e:
                    raise HTTPException(
                        status_code=401,
                        detail=f"Token MCP expiré pour '{n.data.mcp_type}' : {e}",
                    )
 
            specialistes.append(agent)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Configuration agent invalide : {e}")

    def generate():
        try:
            niveau = body.niveau_recherche if body.niveau_recherche in (1, 2, 3) else 1

            orche = Orchestration(
                superviseur=superviseur,
                specialistes=specialistes,
                niveau_recherche=niveau
            )

            final_response = ""

            for event in orche.executer_stream(body.prompt):

                for node_name, state_update in event.items():

                    # Résultat d’un agent spécialiste
                    if "results" in state_update:
                        for agent_nom, content in state_update["results"].items():
                            yield json.dumps({
                                "type": "echange",
                                "agent": agent_nom,
                                "content": content
                            }) + "\n"

                    # Logs du superviseur
                    if "supervisor_logs" in state_update:
                        for log in state_update["supervisor_logs"]:
                            yield json.dumps({
                                "type": "supervisor",
                                "content": log
                            }) + "\n"

                    # Réponse finale
                    if "final_response" in state_update:
                        final_response = state_update["final_response"]
                        yield json.dumps({
                            "type": "final",
                            "response": final_response
                        }) + "\n"

            # Sauvegarde en base après exécution
            try:
                db_save = SessionLocal()
                execution = Execution(
                    workflow_id=body.workflow_id,
                    status="TERMINE",
                    outputs_json={"final_response": final_response}
                )
                db_save.add(execution)
                db_save.commit()
                db_save.close()
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