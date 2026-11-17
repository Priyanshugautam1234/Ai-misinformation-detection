import re
import numpy as np
from typing import List, Dict, Any, Optional
from .embeddings import embedding_engine

class RagasDeepEvalEvaluator:
    """
    RAG Evaluation Engine implementing the standard RAGAS & DeepEval metric specifications:
    1. Faithfulness (Groundedness / Hallucination-free ratio)
    2. Answer Relevance (Semantic alignment with user query)
    3. Context Precision@K (Mean Average Precision of retrieved documents)
    4. Context Recall (Ground-truth attribution coverage)
    5. Hallucination Metric (1.0 - Faithfulness)
    6. Contextual Relevancy (Signal-to-noise ratio in retrieved context)
    """
    def __init__(self, relevance_threshold: float = 0.20):
        self.relevance_threshold = relevance_threshold

    def _split_into_claims(self, text: str) -> List[str]:
        """Splits text into atomic claim statements by sentence and clause boundaries."""
        raw_sentences = re.split(r"[.!?;\n]+", text)
        claims = [s.strip() for s in raw_sentences if len(s.strip().split()) >= 3]
        return claims if claims else [text.strip()]

    def compute_faithfulness(self, generated_answer: str, retrieved_contexts: List[str]) -> Dict[str, Any]:
        """
        RAGAS & DeepEval Faithfulness Metric:
        Proportion of atomic assertions in the generated response that are directly
        grounded in and supported by the retrieved context.
        """
        if not retrieved_contexts or not generated_answer.strip():
            return {"score": 0.0, "total_claims": 0, "grounded_claims": 0, "hallucinated_claims": 0, "unsupported_statements": []}

        claims = self._split_into_claims(generated_answer)
        combined_context = " ".join(retrieved_contexts)
        context_emb = embedding_engine.embed_text(combined_context)
        
        grounded_count = 0
        unsupported = []
        
        for claim in claims:
            claim_emb = embedding_engine.embed_text(claim)
            sim = embedding_engine.cosine_similarity(claim_emb, context_emb)
            
            # Check semantic similarity or exact token overlap
            q_tokens = set(re.findall(r"\b\w{3,}\b", claim.lower()))
            c_tokens = set(re.findall(r"\b\w{3,}\b", combined_context.lower()))
            overlap_ratio = len(q_tokens.intersection(c_tokens)) / len(q_tokens) if q_tokens else 0.0
            
            if sim >= 0.20 or overlap_ratio >= 0.25:
                grounded_count += 1
            else:
                unsupported.append(claim)

        faithfulness_score = grounded_count / len(claims) if claims else 1.0
        
        return {
            "score": round(float(faithfulness_score), 4),
            "total_claims": len(claims),
            "grounded_claims": grounded_count,
            "hallucinated_claims": len(unsupported),
            "unsupported_statements": unsupported
        }

    def compute_answer_relevance(self, query: str, generated_answer: str) -> float:
        """
        RAGAS Answer Relevance Metric:
        Semantic cosine similarity between the user's input query and the generated output.
        """
        if not query.strip() or not generated_answer.strip():
            return 0.0
            
        q_emb = embedding_engine.embed_text(query)
        a_emb = embedding_engine.embed_text(generated_answer)
        sim = embedding_engine.cosine_similarity(q_emb, a_emb)
        
        # Length normalization factor
        word_count = len(generated_answer.split())
        length_penalty = min(1.0, max(0.5, word_count / 8.0))
        
        return round(float(sim * length_penalty), 4)

    def compute_context_precision(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> float:
        """
        RAGAS Context Precision@K Metric:
        Evaluates whether the most relevant documents appear at the top ranks of retrieval.
        Context Precision@K = (Sum of Precision@k * v_k) / Total Relevant Documents
        """
        if not retrieved_docs:
            return 0.0

        q_emb = embedding_engine.embed_text(query)
        relevant_flags = []
        
        for doc in retrieved_docs:
            doc_text = doc.get("text", "")
            d_emb = embedding_engine.embed_text(doc_text)
            sim = embedding_engine.cosine_similarity(q_emb, d_emb)
            is_relevant = 1 if sim >= self.relevance_threshold or doc.get("rerank_score", 0.0) >= 0.15 else 0
            relevant_flags.append(is_relevant)

        total_relevant = sum(relevant_flags)
        if total_relevant == 0:
            return 0.0

        precisions = []
        running_relevant = 0
        for k, flag in enumerate(relevant_flags, start=1):
            if flag == 1:
                running_relevant += 1
                precisions.append(running_relevant / k)

        context_precision = sum(precisions) / total_relevant if precisions else 0.0
        return round(float(context_precision), 4)

    def compute_context_recall(self, ground_truth: str, retrieved_contexts: List[str]) -> float:
        """
        RAGAS & DeepEval Context Recall Metric:
        Proportion of ground-truth statements that can be attributed to the retrieved context.
        """
        if not ground_truth.strip():
            return 1.0
        if not retrieved_contexts:
            return 0.0

        gt_sentences = self._split_into_claims(ground_truth)
        combined_context = " ".join(retrieved_contexts)
        context_emb = embedding_engine.embed_text(combined_context)

        attributed = 0
        for sent in gt_sentences:
            s_emb = embedding_engine.embed_text(sent)
            sim = embedding_engine.cosine_similarity(s_emb, context_emb)
            if sim >= 0.18:
                attributed += 1

        recall_score = attributed / len(gt_sentences) if gt_sentences else 0.0
        return round(float(recall_score), 4)

    def compute_contextual_relevancy(self, query: str, retrieved_contexts: List[str]) -> float:
        """
        DeepEval & G-Eval Contextual Relevancy:
        Signal-to-noise ratio: fraction of sentences in retrieved context that are relevant to the query.
        """
        if not retrieved_contexts or not query.strip():
            return 0.0

        all_sentences = []
        for ctx in retrieved_contexts:
            all_sentences.extend(self._split_into_claims(ctx))

        if not all_sentences:
            return 0.0

        q_emb = embedding_engine.embed_text(query)
        relevant_count = 0
        for sent in all_sentences:
            s_emb = embedding_engine.embed_text(sent)
            if embedding_engine.cosine_similarity(q_emb, s_emb) >= 0.15:
                relevant_count += 1

        return round(float(relevant_count / len(all_sentences)), 4)

    def evaluate_all(self, query: str, generated_answer: str, retrieved_docs: List[Dict[str, Any]], ground_truth: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs the full composite RAGAS & DeepEval evaluation suite on a query-retrieval-answer transaction.
        """
        contexts = [d.get("text", "") for d in retrieved_docs]
        
        faith_res = self.compute_faithfulness(generated_answer, contexts)
        faith_score = faith_res["score"]
        hallucination_score = round(1.0 - faith_score, 4)
        
        ans_relevance = self.compute_answer_relevance(query, generated_answer)
        ctx_precision = self.compute_context_precision(query, retrieved_docs)
        ctx_relevancy = self.compute_contextual_relevancy(query, contexts)
        ctx_recall = self.compute_context_recall(ground_truth or generated_answer, contexts)

        # Composite RAG quality index
        composite_quality = (0.35 * faith_score) + (0.25 * ans_relevance) + (0.20 * ctx_precision) + (0.20 * ctx_recall)

        return {
            "ragas_scores": {
                "faithfulness": faith_score,
                "answer_relevance": ans_relevance,
                "context_precision": ctx_precision,
                "context_recall": ctx_recall
            },
            "deepeval_scores": {
                "hallucination_metric": hallucination_score,
                "contextual_relevancy": ctx_relevancy,
                "grounded_claims_count": faith_res["grounded_claims"],
                "total_claims_evaluated": faith_res["total_claims"]
            },
            "composite_rag_score": round(float(composite_quality), 4),
            "unsupported_assertions": faith_res["unsupported_statements"],
            "verdict": "RELIABLE_GROUNDED" if faith_score >= 0.60 and ans_relevance >= 0.25 else "POTENTIAL_HALLUCINATION_OR_DRIFT"
        }

# Module singleton
rag_evaluator = RagasDeepEvalEvaluator()
