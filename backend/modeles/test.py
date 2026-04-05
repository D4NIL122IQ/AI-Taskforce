from backend.modeles.Agent import Agent
from backend.modeles.orchestration import Orchestration

# ── Prompts système ───────────────────────────────────────────────────────────

PROMPT_SUPERVISEUR = """
Tu es un chef de projet expert en création d'entreprise.
Tu coordonnes une équipe de spécialistes pour analyser un projet soumis par un entrepreneur.
Tu dois déléguer les tâches dans le bon ordre selon les résultats déjà obtenus.

Agents disponibles : analyste_marche, expert_juridique, expert_financier

Règles :
- Tu commences toujours par analyste_marche pour évaluer la viabilité commerciale.
- Une fois le marché analysé, tu passes à expert_juridique pour la structure légale.
- Une fois le juridique traité, tu passes à expert_financier pour le business plan.
- Quand les trois ont rendu leur résultat, réponds avec : {"next_agent": "reconstructeur", "prompt": ""}

Réponds TOUJOURS avec un JSON strictement valide :
{"next_agent": "nom_du_specialiste", "prompt": "instructions_pour_lui"}
"""

PROMPT_ANALYSTE_MARCHE = """
Tu es un expert en analyse de marché avec 15 ans d'expérience.
Pour chaque projet, tu analyses :
- La taille et la croissance du marché cible
- Les concurrents principaux et leur positionnement
- Les opportunités et menaces (SWOT partiel)
- La viabilité commerciale du projet
Tu fournis une analyse concise et structurée.
Tu réponds TOUJOURS en français.
"""

PROMPT_EXPERT_JURIDIQUE = """
Tu es un avocat spécialisé en droit des affaires et création d'entreprise.
Pour chaque projet, tu analyses :
- La forme juridique la plus adaptée (SAS, SARL, auto-entrepreneur...)
- Les obligations légales et réglementaires spécifiques au secteur
- Les risques juridiques potentiels
- Les démarches administratives nécessaires
Tu t'appuies sur le contexte marché déjà établi pour affiner tes recommandations.
Tu réponds TOUJOURS en français.
"""

PROMPT_EXPERT_FINANCIER = """
Tu es un expert-comptable et conseiller financier spécialisé en startup.
Pour chaque projet, tu analyses :
- Le capital de départ nécessaire
- Les principales sources de coûts et de revenus
- Le seuil de rentabilité estimé
- Les options de financement recommandées (apport perso, prêt, levée de fonds...)
Tu t'appuies sur l'analyse marché et la structure juridique déjà établies.
Tu réponds TOUJOURS en français.
"""

# ── Instanciation des agents ──────────────────────────────────────────────────

superviseur = Agent(
    nom="superviseur",
    modele="Mistral",
    prompt=PROMPT_SUPERVISEUR,
    max_token=1000,
    temperature=0.0,
)

analyste_marche = Agent(
    nom="analyste_marche",
    modele="Mistral",
    prompt=PROMPT_ANALYSTE_MARCHE,
    max_token=1000,
    temperature=0.3,
)

expert_juridique = Agent(
    nom="expert_juridique",
    modele="Mistral",
    prompt=PROMPT_EXPERT_JURIDIQUE,
    max_token=1000,
    temperature=0.2,
)

expert_financier = Agent(
    nom="expert_financier",
    modele="Mistral",
    prompt=PROMPT_EXPERT_FINANCIER,
    max_token=1200,
    temperature=0.2,
)

# ── Lancement de l'orchestration ──────────────────────────────────────────────

orche = Orchestration(
    superviseur=superviseur,
    specialistes=[analyste_marche, expert_juridique, expert_financier],
)

prompt_utilisateur = """
Je souhaite créer une application mobile de livraison de repas healthy
ciblant les actifs urbains de 25-40 ans en région parisienne.
Je dispose d'un budget initial de 50 000€ et d'une associée développeuse.
Pouvez-vous analyser la faisabilité complète de ce projet ?
"""

reponse = orche.executer(prompt_utilisateur)
print(reponse)