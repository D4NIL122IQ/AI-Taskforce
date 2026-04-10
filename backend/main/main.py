from api.routers.agent_router import router as agent_router
from fastapi import FastAPI
from api.routers.execution_router import router as execution_router
from backend.appDatabase.init_db import init
from fastapi.middleware.cors import CORSMiddleware
from api.routers.document_router import router as document_router
from api.routers.workflow_router import router as workflow_router
from backend.modeles.Agent import Agent


init()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def welcome_page():
    return {"Page d'accueil"}

app.include_router(agent_router)
app.include_router(workflow_router)
app.include_router(execution_router)
app.include_router(document_router)
