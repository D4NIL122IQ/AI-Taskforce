
from back.modeles.Agent import Agent

ag = Agent("test", "Mistral", "t'es une calculatrice repond que avec la reponse final", 112, 0.1)

rep = ag.executer_prompt("combien font 15 multiplier par 3")

print(rep.content)
