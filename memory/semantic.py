import chromadb
from typing import List
from .interfaces import SemanticMemory
import os

class ChromaSemanticMemory(SemanticMemory):
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="knowledge_base")

    def search(self, query: str, k: int = 3) -> List[str]:
        if self.collection.count() == 0:
            return []
        
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        if results and "documents" in results and results["documents"]:
            return results["documents"][0]
        return []

    def add_documents(self, documents: List[str]) -> None:
        if not documents:
            return
            
        ids = [f"doc_{self.collection.count() + i}" for i in range(len(documents))]
        self.collection.add(
            documents=documents,
            ids=ids
        )
