import unittest
import numpy as np
from app.vector_rag import (
    embedding_engine,
    FAISSVectorIndex,
    QdrantVectorIndex,
    reranker_engine,
    rag_evaluator,
    rag_pipeline
)

class TestVectorRAGPipeline(unittest.TestCase):
    def test_embeddings_generation(self):
        text = "COVID-19 vaccines do not contain 5G microchips."
        vec = embedding_engine.embed_text(text)
        self.assertEqual(len(vec), 384)
        self.assertAlmostEqual(float(np.linalg.norm(vec)), 1.0, places=4)

        # Cosine similarity test
        text_same = "COVID vaccines have no 5G tracking chips."
        text_different = "Chocolate cake recipe with dark cocoa and vanilla."
        vec_same = embedding_engine.embed_text(text_same)
        vec_diff = embedding_engine.embed_text(text_different)

        sim_same = embedding_engine.cosine_similarity(vec, vec_same)
        sim_diff = embedding_engine.cosine_similarity(vec, vec_diff)
        self.assertGreater(sim_same, sim_diff)

    def test_faiss_vector_index(self):
        docs = [
            {"id": "doc1", "title": "5G Vaccine Claim", "text": "Vaccines do not contain microchips or 5G receivers.", "category": "Health"},
            {"id": "doc2", "title": "Volcano Emissions", "text": "Human industry releases 60x more CO2 than all volcanoes combined.", "category": "Climate"}
        ]
        embeddings = embedding_engine.embed_batch([d["text"] for d in docs])
        
        faiss_index = FAISSVectorIndex(embedding_dim=384)
        count = faiss_index.add_documents(docs, embeddings)
        self.assertEqual(count, 2)
        self.assertEqual(faiss_index.count(), 2)

        # Search query
        q_vec = embedding_engine.embed_text("5G chip in vaccine")
        results = faiss_index.search(q_vec, top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["doc_id"], "doc1")
        self.assertGreater(results[0]["similarity_score"], 0.25)

    def test_qdrant_vector_index(self):
        docs = [
            {"id": "qdoc1", "title": "SMS Banking Fraud", "text": "Banks never ask for OTP or passwords via text messages.", "category": "Finance"},
            {"id": "qdoc2", "title": "Spider Sleep Myth", "text": "Humans do not swallow 8 spiders a year in their sleep.", "category": "Biology"}
        ]
        embeddings = embedding_engine.embed_batch([d["text"] for d in docs])
        
        qdrant_index = QdrantVectorIndex(collection_name="test_qdrant_col", embedding_dim=384)
        count = qdrant_index.add_documents(docs, embeddings)
        self.assertEqual(count, 2)
        self.assertEqual(qdrant_index.count(), 2)

        q_vec = embedding_engine.embed_text("Urgent bank text asking for my OTP password")
        results = qdrant_index.search(q_vec, top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["doc_id"], "qdoc1")

    def test_reranker_rrf(self):
        query = "Do vaccines contain 5G microchips?"
        candidates = [
            {"doc_id": "c1", "title": "Volcano facts", "text": "Volcanoes emit CO2 in small amounts.", "similarity_score": 0.55},
            {"doc_id": "c2", "title": "Vaccine microchip facts", "text": "Vaccines contain mRNA and lipids, not microchips or 5G radio components.", "similarity_score": 0.75}
        ]
        reranked = reranker_engine.rerank(query, candidates, top_k=2)
        self.assertEqual(len(reranked), 2)
        self.assertEqual(reranked[0]["doc_id"], "c2")
        self.assertIn("rrf_score", reranked[0])
        self.assertIn("rerank_score", reranked[0])
        self.assertGreaterEqual(reranked[0]["rerank_score"], reranked[1]["rerank_score"])

    def test_ragas_and_deepeval_metrics(self):
        query = "Are 5G chips injected via COVID vaccines?"
        context = ["COVID-19 vaccines do not contain microchips, 5G tracking antennas, or magnetic components. They contain mRNA, lipids, and salts."]
        grounded_answer = "COVID-19 vaccines do not contain 5G tracking antennas or microchips. They are formulated with mRNA and lipids."
        
        retrieved_docs = [{"doc_id": "d1", "text": context[0], "rerank_score": 0.88}]
        
        eval_result = rag_evaluator.evaluate_all(
            query=query,
            generated_answer=grounded_answer,
            retrieved_docs=retrieved_docs,
            ground_truth=context[0]
        )

        ragas = eval_result["ragas_scores"]
        deepeval = eval_result["deepeval_scores"]

        self.assertIn("faithfulness", ragas)
        self.assertIn("answer_relevance", ragas)
        self.assertIn("context_precision", ragas)
        self.assertIn("context_recall", ragas)
        self.assertIn("hallucination_metric", deepeval)

        # High faithfulness and low hallucination on grounded answers
        self.assertGreaterEqual(ragas["faithfulness"], 0.70)
        self.assertLessEqual(deepeval["hallucination_metric"], 0.30)
        self.assertEqual(eval_result["verdict"], "RELIABLE_GROUNDED")

    def test_end_to_end_rag_pipeline(self):
        claim = "Humans swallow eight spiders each year while sleeping."
        result = rag_pipeline.verify_claim(claim, top_k=2, vector_engine="faiss")
        
        self.assertTrue(result["success"])
        self.assertIn("FALSE / MYTH", result["verdict"])
        self.assertGreater(result["confidence"], 0.5)
        self.assertIn("ragas_metrics", result)
        self.assertIn("deepeval_metrics", result)
        self.assertGreater(result["composite_rag_score"], 0.5)
        self.assertGreaterEqual(len(result["retrieved_and_reranked_sources"]), 1)

if __name__ == "__main__":
    unittest.main()
