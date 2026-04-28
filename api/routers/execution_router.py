from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi import Depends
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json
import requests as http_requests
import threading
import queue as queue_module
import time

from backend.appDatabase.database import get_db, SessionLocal
from backend.models.execution_model import Execution
from backend.models.mcp_token_model import McpToken
from backend.modeles.Agent import Agent as AgentLLM
from backend.models.agent_model import Agent
from backend.modeles.orchestration import Orchestration

from fastapi.responses import FileResponse
from backend.services.docx_generator_service import get_document_path, document_existe

from backend.services.mcp_token_service import (
    McpTokenService,
    McpTokenNotFoundError,
    McpTokenExpiredError,
)

router = APIRouter(prefix="/executions", tags=["Executions"])
all_executions = {}      # execution_id → True/False (actif ou stoppé)
execution_queues = {}    # execution_id → queue.Queue (événements produits)
execution_status = {}    # execution_id → "running" | "done" | "error"


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
    generate_document: bool = False

class WorkflowNode(BaseModel):
    id: str
    type: str
    data: NodeData

class ExecuteRequest(BaseModel):
    prompt: str
    nodes: list[WorkflowNode]
    niveau_recherche: int = 1
    workflow_id: int | None = None
    utilisateur_id: str | None = None   # pour résoudre les tokens MCP utilisateur

class McpTokenCreate(BaseModel):
    mcp_type: str       # "github" | "gmail"
    token_public: str
    access_token: str
    refresh_token: str

class PatTokenCreate(BaseModel):
    mcp_type: str   # "github" | "gmail"
    token: str      # Personal Access Token


# ── Endpoint principal ─────────────────────────────────────────────────────────

@router.post("/execute")
def execute_workflow(body: ExecuteRequest, db: Session = Depends(get_db)):
    # Marque l'exécution comme active
    import uuid
    execution_id = str(uuid.uuid4())
    all_executions[execution_id] = True  

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

        mcp_warnings = []
        specialistes = []
        for n in agent_nodes:
            prompt_agent = n.data.system_prompt.strip() or (
                f"Tu es {n.data.label}, un expert en : {n.data.role or n.data.label}. "
                "Réponds de façon précise et structurée."
            )
            try:
                id = db.query(Agent).filter(
                    Agent.nom == n.data.label and 
                    Agent.system_prompt == n.data.system_prompt and 
                    Agent.temperature == n.data.temperature and 
                    Agent.utilisateur_id == body.utilisateur_id
                ).first().id_agent
            except:
                id = -1


            agent = AgentLLM(
                ID = id,
                nom=n.data.label,
                modele=_normalise_modele(n.data.model),
                prompt=prompt_agent,
                max_token=min(n.data.max_tokens, 8192),
                temperature=_clamp(n.data.temperature),
                use_web=n.data.web_search,
                utilise_mcp=n.data.utilise_mcp,
                generate_document=n.data.generate_document,
            )

            # ── Connexion MCP si demandée ─────────────────────────────────────
            print(f"[execution_router] Agent '{n.data.label}' → utilise_mcp={n.data.utilise_mcp}, mcp_type='{n.data.mcp_type}'")
            if n.data.utilise_mcp and n.data.mcp_type:
                if not body.utilisateur_id:
                    mcp_warnings.append(
                        f"⚠ MCP '{n.data.mcp_type}' ignoré pour '{n.data.label}' : utilisateur non identifié."
                    )
                else:
                    try:
                        McpTokenService(db).connecter_agent_mcp(
                            agent=agent,
                            utilisateur_id=body.utilisateur_id,
                            mcp_type=n.data.mcp_type,
                        )
                        print(f"[execution_router] ✓ MCP '{n.data.mcp_type}' connecté pour '{n.data.label}'")
                    except McpTokenNotFoundError:
                        mcp_warnings.append(
                            f"⚠ Token MCP '{n.data.mcp_type}' introuvable pour '{n.data.label}'. "
                            f"Enregistrez votre Personal Access Token GitHub via le panneau MCP."
                        )
                    except McpTokenExpiredError as e:
                        raise HTTPException(
                            status_code=401,
                            detail=f"Token MCP expiré pour '{n.data.mcp_type}' : {e}",
                        )

            specialistes.append(agent)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Configuration agent invalide : {e}")

    # ── Initialisation de la queue pour cet execution_id ──────────────────────
    q = queue_module.Queue()
    execution_queues[execution_id] = q
    execution_status[execution_id] = "running"

    # ── Thread d’arrière-plan : tourne indépendamment de la connexion HTTP ────
    def run_orchestration():
        try:
            # Émettre les warnings MCP en tête
            for w in mcp_warnings:
                q.put(json.dumps({"type": "warning", "message": w}) + "\n")

            niveau = body.niveau_recherche if body.niveau_recherche in (1, 2, 3) else 1

            orche = Orchestration(
                superviseur=superviseur,
                specialistes=specialistes,
                niveau_recherche=niveau
            )

            final_response = ""
            all_echanges = {}

            for event in orche.executer_stream(body.prompt):
                if not all_executions.get(execution_id, False):
                    orche.stop()
                    break

                for node_name, state_update in event.items():
                    if "results" in state_update:
                        for agent_nom, content in state_update["results"].items():
                            all_echanges[agent_nom] = content
                            q.put(json.dumps({"type": "echange", "agent": agent_nom, "content": content}) + "\n")

                    if "supervisor_logs" in state_update:
                        for log in state_update["supervisor_logs"]:
                            q.put(json.dumps({"type": "supervisor", "content": log}) + "\n")

                    # Event parallèle : notifier le frontend
                    if "parallel_tasks" in state_update and state_update["parallel_tasks"]:
                        q.put(json.dumps({"type": "parallel_start", "agents": [t["agent"] for t in state_update[
                            "parallel_tasks"]]}) + "\n")

                    if "documents_generated" in state_update:
                        for doc in state_update["documents_generated"]:
                            q.put(json.dumps({"type": "document", "agent": doc["agent"], "filename": doc["filename"]}) + "\n")

                    if "final_response" in state_update:
                        final_response = state_update["final_response"]
                        q.put(json.dumps({"type": "final", "response": final_response}) + "\n")

            orche.stop_execution = False
            execution_status[execution_id] = "done"
            q.put(None)  # signal de fin

            # Sauvegarde en base après exécution
            try:
                db_save = SessionLocal()
                execution = Execution(
                    workflow_id=body.workflow_id,
                    status="TERMINE",
                    prompt=body.prompt,
                    outputs_json={"final_response": final_response},
                    history_json=all_echanges
                )
                db_save.add(execution)
                db_save.commit()
                db_save.close()
            except Exception as e:
                print("Erreur sauvegarde :", e)

        except Exception as e:
            execution_status[execution_id] = "error"
            q.put(json.dumps({"type": "error", "message": str(e)}) + "\n")
            q.put(None)

    thread = threading.Thread(target=run_orchestration, daemon=True)
    thread.start()

    # ── Retourne l’execution_id immédiatement ──────────────────────────────────
    from fastapi.responses import JSONResponse
    response = JSONResponse(content={"execution_id": execution_id})
    return response

#---------------------mettre fin à l'exécution en cours-------------------------#

@router.post("/stop/{execution_id}")
def stop_execution(execution_id: str):
    if execution_id in all_executions:
        all_executions[execution_id] = False
        print("STOP demandé dans route", flush=True)
        return {"message": "Execution stoppée"}
    return {"message": "Execution non trouvée"}


# Stream reconnectable : le frontend, le changement de page lors de l'execution garde l'execution en back

@router.get("/stream/{execution_id}")
def stream_execution(execution_id: str):
    """
    Endpoint SSE reconnectable.
    Le frontend se connecte ici après avoir reçu l'execution_id.
    Si l'utilisateur change de page et revient, il se reconnecte ici
    et reçoit tous les événements accumulés dans la queue.
    """
    q = execution_queues.get(execution_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Exécution non trouvée ou expirée")

    def generate():
        while True:
            try:
                # timeout=1s pour ne pas bloquer indéfiniment si le thread est mort
                item = q.get(timeout=1)
                if item is None:  # signal de fin
                    # Nettoyer la mémoire après un délai (garder 3 min pour reconnexions tardives)
                    def cleanup():
                        time.sleep(180)
                        execution_queues.pop(execution_id, None)
                        execution_status.pop(execution_id, None)
                        all_executions.pop(execution_id, None)
                    threading.Thread(target=cleanup, daemon=True).start()
                    break
                yield item
            except queue_module.Empty:
                # Si le thread est terminé et la queue vide → on sort
                status = execution_status.get(execution_id)
                if status in ("done", "error"):
                    break
                # Sinon on continue d'attendre (exécution encore en cours)
                continue

    return StreamingResponse(generate(), media_type="application/x-ndjson")


# ── Endpoints MCP tokens (niveau utilisateur) ─────────────────────────────────

@router.get("/mcp-tokens/{utilisateur_id}")
def get_mcp_tokens(utilisateur_id: str, db: Session = Depends(get_db)):
    tokens = McpTokenService(db).get_tokens_for_user(utilisateur_id)
    return [_fmt_mcp(t) for t in tokens]

@router.post("/mcp-tokens/{utilisateur_id}/pat")
def connect_pat(utilisateur_id: str, body: PatTokenCreate, db: Session = Depends(get_db)):
    """Connecte un MCP via Personal Access Token (PAT)."""
    if body.mcp_type == "github":
        resp = http_requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {body.token}", "Accept": "application/json"},
            timeout=10,
        )
        if not resp.ok:
            raise HTTPException(status_code=400, detail="Token GitHub invalide ou insuffisant")
        token_public = resp.json().get("login", "github-user")
    elif body.mcp_type == "gmail":
        resp = http_requests.get(
            "https://www.googleapis.com/oauth2/v3/tokeninfo",
            params={"access_token": body.token},
            timeout=10,
        )
        if not resp.ok:
            raise HTTPException(status_code=400, detail="Token Gmail invalide ou expiré")
        token_public = resp.json().get("email", "gmail-user")
    else:
        raise HTTPException(status_code=400, detail=f"MCP '{body.mcp_type}' non supporté")

    token = McpTokenService(db).creer_ou_remplacer(
        utilisateur_id=utilisateur_id,
        mcp_type=body.mcp_type,
        token_public=token_public,
        access_token=body.token,
        refresh_token="",
    )
    return _fmt_mcp(token)

@router.post("/mcp-tokens/{utilisateur_id}")
def upsert_mcp_token(utilisateur_id: str, body: McpTokenCreate, db: Session = Depends(get_db)):
    token = McpTokenService(db).creer_ou_remplacer(
        utilisateur_id=utilisateur_id,
        mcp_type=body.mcp_type,
        token_public=body.token_public,
        access_token=body.access_token,
        refresh_token=body.refresh_token,
    )
    return _fmt_mcp(token)

@router.delete("/mcp-tokens/{utilisateur_id}/{mcp_type}")
def delete_mcp_token(utilisateur_id: str, mcp_type: str, db: Session = Depends(get_db)):
    deleted = McpTokenService(db).supprimer(utilisateur_id, mcp_type)
    if not deleted:
        raise HTTPException(status_code=404, detail="Token MCP non trouvé")
    return {"message": f"Token {mcp_type} déconnecté"}


# ── CRUD existant ──────────────────────────────────────────────────────────────

@router.get("/")
def get_all_executions(db: Session = Depends(get_db)):
    return [_fmt(e) for e in db.query(Execution).order_by(Execution.date_execution.desc()).all()]

@router.get("/detail/{execution_id}")
def get_execution_detail(execution_id: int, db: Session = Depends(get_db)):
    e = db.query(Execution).filter(Execution.id_execution == execution_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Exécution non trouvée")
    return {
        "id": e.id_execution,
        "workflow_id": e.workflow_id,
        "status": e.status,
        "prompt": e.prompt,
        "echanges": e.history_json or {},
        "reponse_finale": (e.outputs_json or {}).get("final_response", ""),
        "date": e.date_execution.isoformat() if e.date_execution else None,
    }
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




@router.get("/documents/download/{filename}")
def download_document(filename: str):
    if not document_existe(filename):
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return FileResponse(
        path=str(get_document_path(filename)),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

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

def _fmt_mcp(t: McpToken) -> dict:
    return {
        "id": t.id,
        "utilisateur_id": str(t.utilisateur_id),
        "mcp_type": t.mcp_type,
        "token_public": t.token_public,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }