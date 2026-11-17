"""
Vector RAG Module for AI Misinformation & Scam Detection Platform.
Provides:
- Dense Semantic Embeddings (DenseEmbeddingModel)
- Vector Databases (FAISS IndexFlatIP & Qdrant Embedded Vector Engine)
- Hybrid Reranker (Reciprocal Rank Fusion & Cross-Scoring)
- RAGAS & DeepEval Metric Suite (Faithfulness, Answer Relevance, Context Precision, Recall, Hallucination)
- End-to-End Fact-Checking RAG Pipeline
"""

from .embeddings import DenseEmbeddingModel, embedding_engine
from .vector_db import FAISSVectorIndex, QdrantVectorIndex, get_vector_store
from .reranker import RerankerEngine, reranker_engine
from .evaluator import RagasDeepEvalEvaluator, rag_evaluator
from .rag_pipeline import FactCheckingRAGPipeline, rag_pipeline

__all__ = [
    "DenseEmbeddingModel",
    "embedding_engine",
    "FAISSVectorIndex",
    "QdrantVectorIndex",
    "get_vector_store",
    "RerankerEngine",
    "reranker_engine",
    "RagasDeepEvalEvaluator",
    "rag_evaluator",
    "FactCheckingRAGPipeline",
    "rag_pipeline"
]
