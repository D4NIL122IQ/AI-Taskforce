from api.routers.agent_router import router as agent_router
from fastapi import FastAPI
from api.routers.workflow_router import router as workflow_router
from api.routers.user_router import router as user_router
from api.routers.user_router import router as user_router
from api.routers.execution_router import router as execution_router
from backend.appDatabase.init_db import init
from fastapi.middleware.cors import CORSMiddleware
from backend.modeles.Agent import Agent

agent = Agent("assistant", "athene-v2:latest", "tu es un assistant qui repond à des questions diverses", 200, 0.3, use_web=True)

print(agent.executer_prompt("qui est le president actuel du japon ?"))

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
    return {"Page d'accueil":" Welcome sur la page de creation d'agents"}

app.include_router(agent_router)
app.include_router(user_router)
app.include_router(workflow_router)
app.include_router(execution_router)

 