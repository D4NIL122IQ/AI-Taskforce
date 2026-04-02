from backend.modeles.Agent import Agent
from backend.modeles.orchestration import Orchestration

# ── Prompts système ───────────────────────────────────────────────────────────

PROMPT_SUPERVISEUR = """
Tu es un superviseur qui coordonne deux spécialistes.
Agents disponibles : chercheur, redacteur

Règles :
- Tu commences TOUJOURS par chercheur pour collecter les informations.
- Une fois chercheur terminé, tu passes à redacteur pour rédiger la réponse finale.
- Une fois les deux agents terminés, tu termines.

Réponds UNIQUEMENT avec un JSON strictement valide, sans texte autour :
{"next_agent": "nom_du_specialiste", "prompt": "instructions_pour_lui"}

Ou si tout est terminé :
{"next_agent": "reconstructeur", "prompt": ""}
"""

PROMPT_CHERCHEUR = """
Tu es un expert en recherche d'information.
Tu listes des faits précis, concis et structurés sur le sujet qu'on te donne.
Tu réponds TOUJOURS en français, quelle que soit la langue des instructions reçues.
"""

PROMPT_REDACTEUR = """
Tu es un rédacteur professionnel.
Tu prends des notes de recherche et tu les transformes en un texte clair, fluide et convaincant.
Tu réponds TOUJOURS en français, quelle que soit la langue des instructions reçues.
"""

# ── Instanciation des agents ──────────────────────────────────────────────────

superviseur = Agent(
    nom="superviseur",
    modele="Mistral",
    prompt=PROMPT_SUPERVISEUR,
    max_token=500,
    temperature=0.0,
)

chercheur = Agent(
    nom="chercheur",
    modele="Mistral",
    prompt=PROMPT_CHERCHEUR,
    max_token=800,
    temperature=0.3,
)

redacteur = Agent(
    nom="redacteur",
    modele="Mistral",
    prompt=PROMPT_REDACTEUR,
    max_token=800,
    temperature=0.5,
)

# ── Lancement de l'orchestration ──────────────────────────────────────────────

print("[INIT] Création de l'orchestration...")
orche = Orchestration(
    superviseur=superviseur,
    specialistes=[chercheur, redacteur],
)
print("[INIT] Graphe compilé — agents : chercheur, redacteur\n")

prompt_utilisateur = "Trouve 2 avantages de l'hébergement local d'une IA, puis rédige un pitch pour les vendre à un client."

print("=" * 60)
print("PROMPT :", prompt_utilisateur)
print("=" * 60)

reponse = orche.executer(prompt_utilisateur)

print("\n" + "=" * 60)
print("RÉPONSE FINALE :")
print("=" * 60)
print(reponse)