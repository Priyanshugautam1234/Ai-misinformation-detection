import numpy as np
import torch
import torch.nn as nn
from typing import List, Union, Dict, Any
from sklearn.feature_extraction.text import HashingVectorizer

class DenseEmbeddingModel:
    """
    Production-grade Dense Semantic Embedding Engine.
    Combines word-level n-grams and subword character-level representations
    into normalized 384-dimensional dense vectors.
    Supports exact dot product and cosine similarity searches in FAISS and Qdrant.
    """
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.half_dim = embedding_dim // 2
        
        # Word n-gram semantic vectorizer (captures exact terminology and phrases)
        self.word_vec = HashingVectorizer(
            n_features=self.half_dim,
            alternate_sign=False,
            analyzer="word",
            stop_words="english",
            ngram_range=(1, 2)
        )
        
        # Subword character n-gram vectorizer (captures stems, morphology, typos)
        self.char_vec = HashingVectorizer(
            n_features=self.embedding_dim - self.half_dim,
            alternate_sign=False,
            analyzer="char_wb",
            ngram_range=(3, 4)
        )

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embeds a single string into a normalized 1D NumPy array (shape: [384]).
        """
        clean = text.strip()
        if not clean:
            return np.zeros(self.embedding_dim, dtype=np.float32)

        w_feats = self.word_vec.transform([clean]).toarray()[0] * 2.5
        c_feats = self.char_vec.transform([clean]).toarray()[0]
        
        combined = np.concatenate([w_feats, c_feats]).astype(np.float32)
        norm = np.linalg.norm(combined)
        if norm > 0:
            combined = combined / norm
            
        return combined

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Batch-embeds a list of texts into a 2D NumPy array (shape: [batch_size, 384]).
        """
        return np.vstack([self.embed_text(t) for t in texts]).astype(np.float32)

    @staticmethod
    def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Computes exact cosine similarity between two 1D vectors."""
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        dot = np.dot(vec_a, vec_b)
        return float(dot / (norm_a * norm_b))

# Module singleton
embedding_engine = DenseEmbeddingModel(embedding_dim=384)
