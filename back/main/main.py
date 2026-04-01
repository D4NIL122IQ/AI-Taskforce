from back.logic.Agent import Agent
from api.agent_router import router as agent_router
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def say_good_morning():
    return {"Page d'accueil":" Welcome sur la page de creation d'agents"}

app.include_router(agent_router)

#agent = Agent("poly", "UFR", " est de repondre des question sur les maths", 512, 0.2)

#print(agent.executer_prompt("combien font 3 multiplié par 12 ?").content)

#agent._modele = "Mistral"
#print(agent.executerPrompt("quel est ton modèle ollama ou mistral"))
 