from langchain_core.embeddings import Embeddings
from backend.modeles.requestLLM import embed

from concurrent.futures import ThreadPoolExecutor, as_completed
    
class PleiadesEmbeddings(Embeddings):
    def __init__(self, model: str = "nomic-embed-text-v2-moe:latest", max_threads: int = 10):
        self.model = model
        self.max_threads = max_threads

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed en parallèle au lieu de séquentiel."""
        results = [None] * len(texts)
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {
                executor.submit(embed, text, self.model): i 
                for i, text in enumerate(texts)
            }
            for future in as_completed(futures):
                i = futures[future]
                results[i] = future.result()
        
        return results

    def embed_query(self, text: str) -> list[float]:
        return embed(text, model=self.model)