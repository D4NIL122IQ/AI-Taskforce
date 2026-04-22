# backend/services/rag_evaluator.py

import json
from typing import List, Dict
from backend.services.rag_service import RAGService
from backend.modeles.requestLLM import chat

class RAGEvaluator:
    
    """Service pour évaluer la performance du RAG d'un agent.
        l'idee est de créer un dataset de questions-réponses à partir des chunks indexés
        et de mesurer si le RAG retrouve les bons chunks.
        Ensuite, on calcule des métriques classiques : précision, rappel, F1-score.
    """

    def __init__(self, rag_service: RAGService):
        self.rag = rag_service

    # ÉTAPE 1 : Générer des questions depuis les chunks indexés
    def generer_dataset(self, agent_id: int, nb_questions: int = 20) -> List[Dict]:
        """
        Pour chaque chunk, demande au LLM de générer une question
        dont la réponse se trouve dans ce chunk.
        Crée un dataset de référence (question, chunk_attendu)
        """
        # Récupère tous les chunks de cet agent
        collection = self.rag.vectordb._collection
        results = collection.get(
            where={"agent_id": int(agent_id)},
            include=["documents", "metadatas"]
        )

        chunks = results["documents"]
        metadatas = results["metadatas"]

        if not chunks:
            print(f"[Evaluator] Aucun chunk trouvé pour agent_id={agent_id}")
            return []

        # Limiter le nombre de questions
        import random
        indices = random.sample(range(len(chunks)), min(nb_questions, len(chunks)))

        dataset = []
        for i in indices:
            chunk_texte = chunks[i]
            meta = metadatas[i]

            # Demande au LLM de générer une question sur ce chunk
            prompt = f"""Tu es un évaluateur de système RAG.
            Voici un extrait de document :

            \"\"\"{chunk_texte}\"\"\"

                Génère UNE seule question précise dont la réponse se trouve dans cet extrait.
                Réponds uniquement avec la question, sans explication."""

            question = chat(
                message=prompt,
                model="athene-v2:latest",
                temperature=0.2,
                max_tokens=500
            ).strip()

            dataset.append({
                "question": question,
                "chunk_attendu": chunk_texte,
                "chunk_index": meta.get("chunk_index"),
                "doc_id": meta.get("doc_id"),
                "page": meta.get("page")
            })
            print(f"[Evaluator] Question générée : {question[:80]}...")

        return dataset

    # ──────────────────────────────────────────────────────────────────────
    # ÉTAPE 2 : Calcul Précision & Rappel
    # ──────────────────────────────────────────────────────────────────────
    def evaluer(self, agent_id: int, dataset: List[Dict], top_k: int = 5) -> Dict:
        """
        Pour chaque question du dataset :
        - Récupère les top_k chunks via RAG
        - Vérifie si le chunk_attendu est dans les résultats

        Précision = chunks pertinents retrouvés / chunks retrouvés
        Rappel    = chunks pertinents retrouvés / chunks pertinents existants
        """
        vrais_positifs = 0
        faux_positifs = 0
        faux_negatifs = 0

        resultats_detail = []

        for item in dataset:
            question = item["question"]
            chunk_attendu = item["chunk_attendu"]

            # Récupère les chunks via RAG
            chunks_retrouves = self.rag.rechercher(
                agent_id=agent_id,
                question=question,
                top_k=top_k
            )

            # Vérifie si le bon chunk est dans les résultats
            # (similarité textuelle souple — le chunk peut être légèrement reformaté)
            trouve = any(
                self._similarite_texte(chunk_attendu, chunk) > 0.75
                for chunk in chunks_retrouves
            )

            if trouve:
                vrais_positifs += 1
            else:
                faux_negatifs += 1
                faux_positifs += len(chunks_retrouves)  # tous retrouvés sont faux

            resultats_detail.append({
                "question": question,
                "chunk_attendu_extrait": chunk_attendu[:100] + "...",
                "trouve": trouve,
                "nb_chunks_retrouves": len(chunks_retrouves)
            })

        total_retrouves = vrais_positifs + faux_positifs
        total_attendus = len(dataset)

        precision = vrais_positifs / total_retrouves if total_retrouves > 0 else 0
        rappel = vrais_positifs / total_attendus if total_attendus > 0 else 0
        f1 = (2 * precision * rappel / (precision + rappel)) if (precision + rappel) > 0 else 0

        return {
            "precision": round(precision, 3),
            "rappel": round(rappel, 3),
            "f1_score": round(f1, 3),
            "vrais_positifs": vrais_positifs,
            "total_questions": total_attendus,
            "detail": resultats_detail
        }

    # ──────────────────────────────────────────────────────────────────────
    # UTILITAIRE : similarité entre deux textes
    # ──────────────────────────────────────────────────────────────────────
    def _similarite_texte(self, texte1: str, texte2: str) -> float:
        """
        Similarité de Jaccard sur les mots.
        Simple et rapide, pas besoin d'embedding ici.
        """
        mots1 = set(texte1.lower().split())
        mots2 = set(texte2.lower().split())
        intersection = mots1 & mots2
        union = mots1 | mots2
        return len(intersection) / len(union) if union else 0