from backend.services.rag_service import RAGService
import tempfile, os

rag = RAGService()

# 1. Créer un fichier texte de test
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
    f.write("L'intelligence artificielle permet aux machines de simuler l'intelligence humaine. " * 20)
    chemin = f.name

print("Fichier de test :", chemin)

# 2. Tester l'embedding directement
print("\nTest embedding Pleiade...")
vec = rag._generer_embedding("test de connexion Pleiade")
print(f"Vecteur recu : dimension={len(vec)}, premiers vals={vec[:3]}")

# 3. Indexation
print("\nIndexation...")
nb = rag.indexer_document(doc_id=999, agent_id=999, chemin_fichier=chemin)
print(f"{nb} chunks indexes")

# 4. Recherche
print("\nRecherche...")
chunks = rag.rechercher(agent_id=999, question="intelligence artificielle", top_k=2)
print(f"{len(chunks)} chunks trouves")
for i, c in enumerate(chunks, 1):
    print(f"  [{i}] {c[:80]}...")

# 5. Nettoyage
rag.supprimer_document(doc_id=999)
os.unlink(chemin)
print("\nTest termine avec succes !")