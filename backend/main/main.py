from back.modeles.Agent import Agent

agent = Agent("poly", "Mistral", " est de repondre des question sur les maths", 512, 0.2)

print(agent.executer_prompt("combien font 3 multiplié par 12 ?").content)

#agent._modele = "Mistral"
#print(agent.executerPrompt("quel est ton modèle ollama ou mistral"))
 