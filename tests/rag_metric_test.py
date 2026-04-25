# backend/tests/test_rag_metrics.py

import requests
import os
from backend.services.rag_service import RAGService
from tests.rag_evaluation_service import RAGEvaluator

AGENT_ID = 158 # ← ton agent avec des documents indexés

rag = RAGService()
evaluator = RAGEvaluator(rag)

# 1. Génère le dataset
print("=== Génération du dataset ===")
dataset = evaluator.generer_dataset(agent_id=AGENT_ID, nb_questions=20)

# Sauvegarde le dataset pour le réutiliser
import json
with open("dataset_eval.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

# 2. Évalue
print("\n=== Évaluation RAG ===")
metriques = evaluator.evaluer(agent_id=AGENT_ID, dataset=dataset, top_k=5)

print(f"\n Résultats :")
print(f"  Précision : {metriques['precision']:.1%}")
print(f"  Rappel    : {metriques['rappel']:.1%}")
print(f"  F1-Score  : {metriques['f1_score']:.1%}")
print(f"  Chunks trouvés : {metriques['vrais_positifs']}/{metriques['total_questions']}")

print(f"\n Détail par question :")
for r in metriques["detail"]:
    statut = "OK" if r["trouve"] else "NN"
    print(f"  {statut} {r['question'][:70]}...")