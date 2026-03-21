from back.modeles.Agent import Agent

agent = Agent("poly", "Ollama", " calculatrice de base", 12, 0.1)

print(agent.executer_prompt("combien font 12 multiplié par 3").content)

#agent._modele = "Mistral"
#print(agent.executerPrompt("quel est ton modèle ollama ou mistral"))
