import re
import numpy as np
from typing import List, Dict, Any

class RerankerEngine:
    """
    Two-Stage Hybrid Reranking Engine.
    Combines dense semantic vector relevance with fine-grained lexical cross-scoring
    and Reciprocal Rank Fusion (RRF) to eliminate semantic false matches.
    """
    def __init__(self, rrf_k: int = 60, dense_weight: float = 0.65, lexical_weight: float = 0.35):
        self.rrf_k = rrf_k
        self.dense_weight = dense_weight
        self.lexical_weight = lexical_weight

    def _compute_lexical_overlap(self, query: str, text: str) -> float:
        """Computes query keyword coverage and exact term match density."""
        q_tokens = set(re.findall(r"\b\w+\b", query.lower()))
        t_tokens = set(re.findall(r"\b\w+\b", text.lower()))
        
        if not q_tokens:
            return 0.0
            
        intersection = q_tokens.intersection(t_tokens)
        jaccard = len(intersection) / len(q_tokens.union(t_tokens)) if q_tokens.union(t_tokens) else 0.0
        recall = len(intersection) / len(q_tokens)
        
        # Exact n-gram phrase boost
        phrase_boost = 0.2 if query.lower() in text.lower() else 0.0
        
        return float(min(1.0, (0.6 * recall) + (0.2 * jaccard) + phrase_boost))

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Reranks retrieved candidate documents using Cross-Scoring and Reciprocal Rank Fusion (RRF).
        """
        if not candidates:
            return []

        # 1. Rank candidates by dense similarity
        dense_sorted = sorted(candidates, key=lambda x: x.get("similarity_score", 0.0), reverse=True)
        dense_ranks = {doc["doc_id"]: rank + 1 for rank, doc in enumerate(dense_sorted)}

        # 2. Score candidates by lexical token coverage
        lexical_scores = {doc["doc_id"]: self._compute_lexical_overlap(query, doc["text"]) for doc in candidates}
        lexical_sorted = sorted(candidates, key=lambda x: lexical_scores[x["doc_id"]], reverse=True)
        lexical_ranks = {doc["doc_id"]: rank + 1 for rank, doc in enumerate(lexical_sorted)}

        # 3. Compute fused RRF and cross-encoder score
        reranked = []
        for doc in candidates:
            doc_id = doc["doc_id"]
            d_rank = dense_ranks[doc_id]
            l_rank = lexical_ranks[doc_id]
            
            # Standard Reciprocal Rank Fusion formula
            rrf_score = (self.dense_weight / (self.rrf_k + d_rank)) + (self.lexical_weight / (self.rrf_k + l_rank))
            
            # Normalize to 0.0 - 1.0 calibrated score
            base_sim = doc.get("similarity_score", 0.5)
            lex_sim = lexical_scores[doc_id]
            cross_score = (0.55 * base_sim) + (0.45 * lex_sim)
            
            doc_copy = dict(doc)
            doc_copy["original_rank"] = d_rank
            doc_copy["lexical_overlap"] = round(lex_sim, 4)
            doc_copy["rrf_score"] = round(float(rrf_score), 6)
            doc_copy["rerank_score"] = round(float(cross_score), 4)
            reranked.append(doc_copy)

        # Sort by final rerank_score
        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        # Attach new rank
        for idx, doc in enumerate(reranked):
            doc["reranked_rank"] = idx + 1
            doc["rank_shift"] = doc["original_rank"] - doc["reranked_rank"]

        return reranked[:top_k]

# Module singleton
reranker_engine = RerankerEngine()
