# 🧠 AI Workflow Builder (Système Multi-Agents)

Un projet de création de workflows IA basé sur un **graphe**, utilisant un **agent superviseur** pour orchestrer des agents spécialisés.

Ce système permet de construire et exécuter des workflows où un superviseur découpe une tâche en sous-tâches et les assigne automatiquement aux agents les plus adaptés.

---

## 🚀 Fonctionnalités

* 🧩 Système de workflow basé sur un graphe
* 🤖 Architecture multi-agents (Superviseur + Spécialistes)
* 🧠 Découpage automatique des tâches
* 🔀 Routing dynamique des tâches
* ⚡ Exécution parallèle (async)
* 🔍 Logs d’exécution (basique)
* 🧪 API simple pour tester les workflows

---

## 🏗️ Stack technique

### Backend

* Python
* FastAPI
* LangGraph
* LangChain

### Frontend

* React 19
* Vite
* Tailwind CSS
* React Router DOM
* Axios

---

## 📦 Installation

### 1. Cloner le projet

```bash id="clone"
git clone https://github.com/D4NIL122IQ/AI-Taskforce.git
cd AI-Taskforce
```

---

### 2. Créer un environnement virtuel

```bash id="venv"
python -m venv venv
source venv/bin/activate  # Linux / Mac
source venv/Scripts/activate # Windows
```

---

### 3. Installer les dépendances

```bash id="install"
pip install -r requirements.txt
```

---

## ▶️ Lancer le projet

### Backend

```bash id="run"
uvicorn app.main:app --reload
```

Documentation API disponible sur :

```
http://localhost:8000/docs
```

### Frontend

#### 1. Aller dans le dossier frontend

```bash
cd frontend
```

#### 2. Installer les dépendances

```bash
npm install
```

#### 3. Lancer le serveur de développement

```bash
npm run dev
```

L'application est disponible sur :

```
http://localhost:5173
```
---

## 🧠 Fonctionnement

1. L’utilisateur envoie un prompt
2. Le superviseur :

   * découpe la tâche en sous-tâches
   * assigne chaque tâche à un agent spécialisé
3. Les agents exécutent les tâches
4. Les résultats sont agrégés et retournés

---

## 📄 Exemple de workflow (JSON)

```json id="example"
{
  "id": "flow_1",
  "input": {
    "prompt": "Ecrire un algorithme de tri"
  },
  "nodes": [
    {
      "id": "supervisor",
      "type": "supervisor"
    },
    {
      "id": "dev",
      "type": "agent",
      "role": "developer"
    }
  ],
  "edges": [
    {
      "source": "supervisor",
      "target": "dev"
    }
  ]
}
```

---

## 📂 Structure du projet

```id="structure"
app/
 ├── api/
 ├── services/
 ├── langgraph/
 ├── models/
 ├── schemas/
 └── main.py
```

---

---

## 🛠️ Améliorations futures

* Ajouter une base de données (PostgreSQL)
* Ajouter l’authentification
* Versioning des workflows
* Streaming en temps réel
* Outils avancés de debug

---

### Exécuter un workflow

```bash id="api"
POST /execute
```

Body :

```json id="body"
{
  "prompt": "Créer une API REST en Python"
}
```

---

---

🔥 Projet conçu en L3 a upc
