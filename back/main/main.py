from back.logic.Agent import Agent

agent = Agent("poly", "Ollama", " tu repond des question sur l'eau et son changement d'Etat", 512, 0.2)

print(agent.executer_prompt(" quelle est la temperature d'ébulution de l'eau ?").content)

#agent._modele = "Mistral"
#print(agent.executerPrompt("quel est ton modèle ollama ou mistral"))
