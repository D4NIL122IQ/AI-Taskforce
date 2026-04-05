# AI Workflow Builder — Système Multi-Agents

Un système d'orchestration multi-agents basé sur **LangGraph**. L'utilisateur construit un workflow sous forme de graphe, un **superviseur** décompose la requête en sous-tâches et les délègue à des agents spécialisés. Un **reconstructeur** synthétise la réponse finale.

---

## Fonctionnalités

- Architecture multi-agents : Superviseur → Spécialistes → Reconstructeur
- Routing dynamique des tâches via LangGraph
- Paramètre `niveau_recherche` (1/2/3) : contrôle le nombre d'appels LLM par sous-tâche pour affiner les réponses
- Support de l'API **Pléiade** (Université Paris Descartes, format OpenAI-compatible)
- Chargement de documents contextuels par agent (PDF, TXT, CSV)
- Interface React avec canvas ReactFlow pour créer et visualiser les workflows
- API REST FastAPI pour la gestion des agents et workflows (PostgreSQL)

---

## Stack technique

### Backend
- Python 3.13
- FastAPI
- LangGraph / LangChain
- PostgreSQL (SQLAlchemy)
- API Pléiade (`pleiade.mi.parisdescartes.fr`)

### Frontend
- React 19 + Vite
- Tailwind CSS
- @xyflow/react (ReactFlow)
- React Router DOM

---

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/D4NIL122IQ/AI-Taskforce.git
cd AI-Taskforce
```

### 2. Créer l'environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / Mac
source .venv/Scripts/activate    # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

```env
TOKEN_PLEIADE=your_token_here
```

---

## Lancer le projet

### Backend

```bash
uvicorn backend.main.main:app --reload
```

Documentation API : `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Application disponible sur : `http://localhost:5173`

### Tester l'orchestration directement

```bash
python -m backend.modeles.test_orchestration
```

---

## Fonctionnement

```
Prompt utilisateur
      ↓
[Superviseur] — décompose la tâche, route vers les spécialistes
      ↓
[Spécialiste 1] → résultat 1
[Spécialiste 2] → résultat 2
      ↓
[Reconstructeur] — synthétise la réponse finale
```

### Niveau de recherche

Le paramètre `niveau_recherche` contrôle la profondeur d'analyse par sous-tâche :

| Niveau | Comportement |
|--------|-------------|
| 1 | 1 appel LLM par sous-tâche (rapide) |
| 2 | jusqu'à 2 appels — le superviseur peut affiner la réponse d'un agent |
| 3 | jusqu'à 3 appels — meilleure qualité |

```python
orche = Orchestration(superviseur, specialistes, niveau_recherche=3)
reponse = orche.executer("Mon prompt")
```

---

## Structure du projet

```
AI-Taskforce/
├── backend/
│   ├── modeles/          # Moteur d'orchestration
│   │   ├── Agent.py          # Classe agent (Pléiade)
│   │   ├── orchestration.py  # Point d'entrée orchestration
│   │   ├── graphBuilder.py   # State machine LangGraph
│   │   ├── requestLLM.py     # Client API Pléiade
│   │   └── LLMFactory.py     # Factory LLM (autres providers)
│   ├── models/           # ORM SQLAlchemy
│   ├── route/            # Endpoints FastAPI
│   ├── schemas/          # Schémas Pydantic
│   ├── services/         # Logique métier
│   └── appDatabase/      # Config PostgreSQL
├── frontend/             # Interface React
├── tests/                # Tests unitaires
├── patern.json           # Exemple de workflow JSON
└── .env                  # Variables d'environnement (non versionné)
```

---

## Exemple de workflow JSON

```json
{
  "id": "flow_1",
  "orchestration": {
    "niveau_recherche": 2
  },
  "input": {
    "prompt": "Analyse les tendances IA en 2025"
  },
  "nodes": [
    {
      "id": "superviseur",
      "type": "supervisor",
      "data": {
        "model": "Pleiade",
        "system_prompt": "Tu es un superviseur...",
        "max_tokens": 500,
        "temperature": 0.0
      }
    },
    {
      "id": "chercheur",
      "type": "agent",
      "data": {
        "model": "Pleiade",
        "system_prompt": "Tu es un expert en recherche...",
        "max_tokens": 800,
        "temperature": 0.3
      }
    }
  ]
}
```

---

## Améliorations prévues

- Endpoint `/execute` pour déclencher l'orchestration via API
- Connexion frontend ↔ backend (remplacement du localStorage)
- Streaming temps réel (WebSocket / SSE)
- Authentification utilisateurs
- Versioning des workflows

---

Projet développé en L3 — Université Paris Cité (UPC)