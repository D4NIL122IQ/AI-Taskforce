
from api.agent_router import router as agent_router
from fastapi import FastAPI
from api.user_router import router as user_router
from backend.modeles.Agent import Agent

app = FastAPI()

@app.get("/")
def welcome_page():
    return {"Page d'accueil":" Welcome sur la page de creation d'agents"}

app.include_router(agent_router)
app.include_router(user_router)

agent = Agent("poly", "Ollama", " est de repondre des question sur les maths", 512, 0.2)

print(agent.executer_prompt("combien font 3 multiplié par 12 ?").content)

#agent._modele = "Mistral"
#print(agent.executerPrompt("quel est ton modèle ollama ou mistral"))
 