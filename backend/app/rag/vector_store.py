import os
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from backend.app.core.config import settings

class LocalEmbeddingFunction(chromadb.EmbeddingFunction):
    """
    Wrapper for sentence-transformers to integrate with ChromaDB's embedding API.
    Computes text embeddings locally.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # This will download the model to cache on first use (approx 90MB)
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: List[str]) -> List[List[float]]:
        # Encodes the input texts into vector embeddings
        embeddings = self.model.encode(input)
        return embeddings.tolist()

    @staticmethod
    def name() -> str:
        return "local_sentence_transformer"

    def get_config(self) -> dict:
        return {"model_name": self.model_name}

    @staticmethod
    def build_from_config(config: dict) -> "LocalEmbeddingFunction":
        return LocalEmbeddingFunction(model_name=config.get("model_name", "all-MiniLM-L6-v2"))

class VectorStoreManager:
    _client = None
    _collection = None
    _embedding_function = None
    
    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        return cls._client
        
    @classmethod
    def get_embedding_function(cls):
        if cls._embedding_function is None:
            cls._embedding_function = LocalEmbeddingFunction()
        return cls._embedding_function

    @classmethod
    def get_collection(cls, collection_name: str = "medical_guidelines"):
        """Initializes or retrieves the vector collection with the local embedding function."""
        if cls._collection is None:
            client = cls.get_client()
            embedding_fn = cls.get_embedding_function()
            # Register local embedding function directly with ChromaDB collection
            cls._collection = client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_fn
            )
        return cls._collection

    @classmethod
    def add_documents(cls, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Ingests list of text documents into the vector index."""
        collection = cls.get_collection()
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    @classmethod
    def search(cls, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Performs semantic vector search for a given clinical query.
        Returns: List of dicts containing document text, source metadata, and distance.
        """
        collection = cls.get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        parsed_results = []
        if not results or not results["documents"]:
            return parsed_results
            
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        ids = results["ids"][0]
        distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
        
        for i in range(len(docs)):
            parsed_results.append({
                "id": ids[i],
                "text": docs[i],
                "metadata": metas[i],
                "score": float(distances[i])
            })
            
        return parsed_results
