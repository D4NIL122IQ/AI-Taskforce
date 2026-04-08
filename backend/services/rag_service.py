# backend/services/rag_service.py

import os
from typing import List
from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_db")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

EMBEDDING_MODEL = "nomic-embed-text"


class RAGService:
    def __init__(self):
        self.embedding = OllamaEmbeddings(model=EMBEDDING_MODEL)

        self.vectordb = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=self.embedding
        )

    # =============================
    # EXTRACTION
    # =============================
    def _extraire_texte(self, chemin: str) -> str:
        if not os.path.exists(chemin):
            raise FileNotFoundError(chemin)

        ext = os.path.splitext(chemin)[1].lower()

        if ext in (".txt", ".md"):
            return open(chemin, "r", encoding="utf-8").read()

        elif ext == ".pdf":
            reader = PdfReader(chemin)
            return "\n".join(page.extract_text() or "" for page in reader.pages)

        elif ext == ".docx":
            from docx import Document as DocxDocument
            doc = DocxDocument(chemin)
            return "\n".join(p.text for p in doc.paragraphs)

        else:
            raise ValueError(f"Format non supporté : {ext}")

    # =============================
    # CHUNKS
    # =============================
    def _decouper_en_chunks(self, texte: str) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""]
        )

        return splitter.create_documents([texte]) 

    # =============================
    # INDEXATION
    # =============================
    def indexer_document(self, doc_id: int, agent_id: int, chemin_fichier: str) -> int:
        print(f"[RAGService] Indexation doc_id={doc_id}, agent_id={agent_id}...")

        texte = self._extraire_texte(chemin_fichier)

        if not texte.strip():
            return 0

        documents = self._decouper_en_chunks(texte)

        # Ajouter metadata
        for i, doc in enumerate(documents):
            doc.metadata = {
                "doc_id": doc_id,
                "agent_id": agent_id,
                "chunk_index": i,
                "chemin": chemin_fichier
            }

        self.vectordb.add_documents(documents)

        print(f"[RAGService]  {len(documents)} chunks indexés.")
        return len(documents)

    # =============================
    # RECHERCHE
    # =============================
    def rechercher(self, agent_id: int, question: str, top_k: int = 5) -> List[str]:
        if not question.strip():
            return []

        """
            Algorithme de MMR pour la diversifier les documents retournés par la recherche 

        """
        docs =[]
        results = self.vectordb.max_marginal_relevance_search(
            query=question,
            k=5,
            fetch_k=30,
            lambda_mult=0.5,
            filter={"agent_id": agent_id}  
        )

        retriever = self.vectordb.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 30}
        )
        
        rep = retriever.invoke(question)
                
        for doc in results:
            docs.append(doc.page_content)
        docs.append("\n********************************************* retrieva\n")
        
        for doc in rep:
            docs.append(doc.page_content)
        return docs

    # =============================
    # CONTEXTE
    # =============================
    def contexte_pour_prompt(self, agent_id: int, question: str, top_k: int = 5) -> str:
        chunks = self.rechercher(agent_id, question, top_k)

        if not chunks:
            return ""

        return "\n\n".join(chunks)

    # =============================
    # DELETE
    # =============================
    def supprimer_document(self, doc_id: int):
        self.vectordb._collection.delete(where={"doc_id": doc_id})

    def supprimer_agent(self, agent_id: int):
        self.vectordb._collection.delete(where={"agent_id": agent_id})