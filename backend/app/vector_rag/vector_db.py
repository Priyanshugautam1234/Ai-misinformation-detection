import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import faiss
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

class BaseVectorStore:
    """Abstract interface for dense Vector Databases."""
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray) -> int:
        raise NotImplementedError

    def search(self, query_vector: np.ndarray, top_k: int = 5, filter_meta: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError

class FAISSVectorIndex(BaseVectorStore):
    """
    FAISS (Facebook AI Similarity Search) Flat Inner Product Vector Index.
    With L2-normalized vectors, Inner Product is mathematically identical to Cosine Similarity.
    """
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        # IndexFlatIP gives exact cosine similarity on normalized vectors
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.documents: Dict[int, Dict[str, Any]] = {}
        self._next_id = 0

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray) -> int:
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings.")
            
        # Ensure float32 format for FAISS
        embeddings = np.ascontiguousarray(embeddings.astype(np.float32))
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Register document metadata mapped to integer index ID
        added_count = 0
        for doc in documents:
            doc_id = self._next_id
            self.documents[doc_id] = {
                "id": doc.get("id", str(doc_id)),
                "title": doc.get("title", "Untitled Document"),
                "text": doc.get("text", ""),
                "category": doc.get("category", "General"),
                "source": doc.get("source", "FactCheck Central"),
                "verdict": doc.get("verdict", "UNVERIFIED"),
                "metadata": doc.get("metadata", {})
            }
            self._next_id += 1
            added_count += 1
            
        return added_count

    def search(self, query_vector: np.ndarray, top_k: int = 5, filter_meta: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []
            
        top_k = min(top_k, self.index.ntotal)
        query_vector = np.ascontiguousarray(query_vector.reshape(1, -1).astype(np.float32))
        
        # FAISS search: returns similarities and index IDs
        similarities, indices = self.index.search(query_vector, top_k)
        
        results = []
        for sim, idx in zip(similarities[0], indices[0]):
            if idx == -1 or idx not in self.documents:
                continue
            doc = dict(self.documents[idx])
            
            # Metadata filter check
            if filter_meta:
                match = True
                for k, v in filter_meta.items():
                    if doc.get(k) != v and doc.get("metadata", {}).get(k) != v:
                        match = False
                        break
                if not match:
                    continue
                    
            results.append({
                "doc_id": doc["id"],
                "title": doc["title"],
                "text": doc["text"],
                "category": doc["category"],
                "source": doc["source"],
                "verdict": doc["verdict"],
                "similarity_score": round(float(sim), 4),
                "engine": "FAISS IndexFlatIP"
            })
            
        return results

    def count(self) -> int:
        return self.index.ntotal

class QdrantVectorIndex(BaseVectorStore):
    """
    Qdrant Embedded Vector Database with Cosine Distance Metric and Rich Payloads.
    Runs locally in-memory or on-disk with fast metadata filtering.
    """
    def __init__(self, collection_name: str = "misinformation_knowledge", embedding_dim: int = 384):
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        # Local fast in-memory Qdrant instance
        self.client = QdrantClient(":memory:")
        self._init_collection()
        self._doc_counter = 0

    def _init_collection(self):
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE)
        )

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray) -> int:
        points = []
        for i, doc in enumerate(documents):
            self._doc_counter += 1
            point_id = self._doc_counter
            vector = embeddings[i].tolist()
            payload = {
                "doc_id": doc.get("id", str(point_id)),
                "title": doc.get("title", "Untitled Document"),
                "text": doc.get("text", ""),
                "category": doc.get("category", "General"),
                "source": doc.get("source", "FactCheck Central"),
                "verdict": doc.get("verdict", "UNVERIFIED"),
                "metadata": doc.get("metadata", {})
            }
            points.append(PointStruct(id=point_id, vector=vector, payload=payload))

        self.client.upsert(collection_name=self.collection_name, points=points)
        return len(points)

    def search(self, query_vector: np.ndarray, top_k: int = 5, filter_meta: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query_list = query_vector.flatten().tolist()
        
        qdrant_filter = None
        if filter_meta:
            conditions = []
            for k, v in filter_meta.items():
                conditions.append(FieldCondition(key=k, match=MatchValue(value=v)))
            if conditions:
                qdrant_filter = Filter(must=conditions)

        # Qdrant query_points (compatible with qdrant-client >= 1.10)
        res = self.client.query_points(
            collection_name=self.collection_name,
            query=query_list,
            query_filter=qdrant_filter,
            limit=top_k
        )

        results = []
        for point in res.points:
            p = point.payload or {}
            results.append({
                "doc_id": p.get("doc_id", str(point.id)),
                "title": p.get("title", ""),
                "text": p.get("text", ""),
                "category": p.get("category", ""),
                "source": p.get("source", ""),
                "verdict": p.get("verdict", ""),
                "similarity_score": round(float(point.score), 4),
                "engine": "Qdrant Vector Engine"
            })
            
        return results

    def count(self) -> int:
        info = self.client.get_collection(collection_name=self.collection_name)
        return info.points_count or 0

def get_vector_store(engine_type: str = "faiss", embedding_dim: int = 384) -> BaseVectorStore:
    """Factory helper to obtain the selected vector engine."""
    engine_lower = engine_type.lower()
    if "qdrant" in engine_lower:
        return QdrantVectorIndex(embedding_dim=embedding_dim)
    return FAISSVectorIndex(embedding_dim=embedding_dim)
