# État d'avancement — AI-Taskforce (Orchestration Multi-Agents)

> Fichier de suivi interne. Mis à jour au fil des sessions de travail.
> Dernière mise à jour : 2026-04-04

---

## Objectif du projet

Système d'orchestration multi-agents basé sur LangGraph :
- L'utilisateur crée des agents (rôles, LLM, prompt système) et des workflows (graphe de nœuds)
- Un **superviseur** décompose la tâche, délègue aux agents spécialistes, puis un **reconstructeur** synthétise la réponse finale
- Interface React pour créer, visualiser et exécuter les workflows en temps réel

**Stack :** FastAPI + LangGraph + LangChain | React 19 + ReactFlow + Tailwind | PostgreSQL

---

## Architecture cible

```
[Frontend]
  CreatAgentPage → CreatWorkflowPage → ExecuteWorkflowPage
        ↓ (API calls — MANQUANT)
[Backend FastAPI]
  POST /execute → Orchestration Engine
        ├─ Supervisor (LangGraph)
        ├─ Specialist Agents (LLMFactory)
        └─ Reconstructor
        ↓
  PostgreSQL (models définis, pas encore connectés)
```

---

## Ce qui est FAIT ✅

### Backend — Moteur d'orchestration
- [x] `Agent.py` — Classe agent avec config LLM dynamique + chargement documents (PDF, TXT, CSV)
- [x] `LLMFactory.py` — Factory multi-provider : OpenAI, Claude, Gemini, Ollama, Mistral, DeepSeek
- [x] `orchestration.py` — Moteur superviseur + spécialistes
- [x] `graphBuilder.py` — Construction du state machine LangGraph (supervisor → specialist → reconstructor)
- [x] `parserData.py` — Parse un JSON workflow → instancie les agents (modifié récemment)
- [x] `Message.py` — Classe message avec enum de types
- [x] `patern.json` — Exemple de structure de workflow JSON

### Backend — Modèles BDD (SQLAlchemy ORM)
- [x] `workflow_model.py` — Entité Workflow avec stockage graphe JSON
- [x] `agent_model.py` — Entité Agent (contraintes température 0-1, max_tokens 1-8192)
- [x] `execution_model.py` — Suivi d'exécutions (historique + sorties JSON)
- [x] `etape_model.py` — Étapes workflow avec machine d'état (EN_ATTENTE → EN_COURS → TERMINE/ERREUR)
- [x] `message_model.py`, `utilisateur_model.py`, `document_model.py`

### Backend — Routes & Services
- [x] `workflow_route.py` — Endpoints REST CRUD pour les workflows
- [x] `workflow_service.py` — Couche service pour opérations BDD
- [x] `database.py` — Config connexion PostgreSQL

### Frontend
- [x] `HomePage.jsx` — Page d'accueil avec features
- [x] `CreatAgentPage.jsx` — Formulaire création agent (modifié récemment) :
  - Sélection modèle LLM, température, max_tokens
  - Prompt système, rôle superviseur auto-rempli
  - Upload documents drag-and-drop
- [x] `CreatWorkflowPage.jsx` — Canvas ReactFlow pour construire workflows
- [x] `ExecuteWorkflowPage.jsx` — Visualisation animée de l'exécution :
  - Canvas ReactFlow avec nœuds animés
  - Panel chat temps réel (superviseur/agents)
  - **SIMULÉ** — pas encore connecté au backend
- [x] `GestionAgentPage.jsx` — Dashboard gestion agents
- [x] Composants UI : NavBar, ThemeContext (dark/light), PageBackground, Button...

### Tests
- [x] `test_agent.py`, `test_orchestration.py`, `parserData_test.py`, `LLMFactory_test.py`

---

## Ce qui est EN COURS / INCOMPLET ⚠️

### Critique — Intégration Frontend ↔ Backend
- [ ] **Aucun appel API depuis le frontend** — tout est en localStorage
- [ ] **Pas d'endpoint `/execute`** qui lance l'orchestration réelle
- [ ] **Pas de couche axios/fetch** dans le frontend pour communiquer avec FastAPI
- [ ] `ExecuteWorkflowPage.jsx` affiche "(Résultat simulé — backend requis)"

### Backend
- [ ] **`writerData.py` cassé** — `def writeFile(Filepath)` sans deux-points ni corps, fonctions `writeAgent()`, `writeRespons()`, `writePrompt()` vides
- [ ] **Pas de `main.py` FastAPI fonctionnel** — point d'entrée de l'app non visible/absent
- [ ] La BDD est configurée mais **pas activement utilisée** (routes non montées sur l'app)
- [ ] Credentials BDD en clair dans `database.py` : `passer123@localhost:5432`

### Frontend
- [ ] Route `/agents/edit/:id` définie mais pas de page `EditAgentPage`
- [ ] Pas de système d'auth (page `/auth` existe mais backend absent)
- [ ] Pas de gestion d'erreurs pour les échecs backend

### Bugs connus
- [ ] `LLMFactory.py` : option "mistral" utilise `ChatOllama` au lieu de l'API Mistral directe
- [ ] Référence à un ancien modèle Claude : `claude-3-haiku-20240307` (outdated)

---

## Ce qui N'EST PAS COMMENCÉ ❌

- [ ] Authentification utilisateurs (JWT / sessions)
- [ ] Streaming temps réel des réponses agents (WebSocket ou SSE)
- [ ] Versioning des workflows
- [ ] Gestion d'erreurs production-ready
- [ ] Déploiement / Docker / CI-CD

---

## Prochaines étapes prioritaires

1. **Créer `main.py`** — point d'entrée FastAPI qui monte toutes les routes
2. **Endpoint `/execute`** — reçoit un workflow JSON + message utilisateur → lance l'orchestration → retourne le résultat
3. **Couche API frontend** — service axios qui appelle le backend depuis React
4. **Connecter `ExecuteWorkflowPage`** — remplacer la simulation par de vrais appels API
5. **Activer la BDD** — brancher les services sur les routes, tester la persistance

---

## Fichiers modifiés récemment (git status au 2026-04-04)

- `backend/modeles/parserData.py` — modifié
- `frontend/src/pages/CreatAgentPage.jsx` — modifié
- Nouveaux fichiers non commités :
  - `backend/modeles/__init__.py`
  - `backend/modeles/test.py`
  - `backend/route/` (nouveau dossier)
  - `backend/schemas/` (nouveau dossier)
  - `backend/services/__init__.py`
  - `backend/services/workflow_service.py`
  - `backend/test_request.py`