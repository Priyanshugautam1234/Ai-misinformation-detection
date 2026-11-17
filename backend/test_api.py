import unittest
from fastapi.testclient import TestClient
from app.main import app
import json
import io

class TestMisinfoShieldAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("docs", data)

    def test_system_status(self):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data)
        self.assertIn("modules", data)

    def test_text_claim_analysis_valid(self):
        payload = {"text": "This is a dramatic conspiracy clickbait claim showing that scientists are quiet about a miracle cure!"}
        response = self.client.post("/api/analyze/text", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("trust_score", data)
        self.assertIn("metrics", data)
        self.assertIn("clickbait_score", data["metrics"])
        self.assertGreater(data["metrics"]["clickbait_score"], 20)

    def test_text_claim_analysis_too_short(self):
        payload = {"text": "short"}
        response = self.client.post("/api/analyze/text", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_image_forensics_upload(self):
        # Create a mock transparent JPEG image in bytes
        # 1x1 white pixel JPEG bytes
        mock_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9'
        
        file_payload = {"file": ("test_deepfake.jpg", mock_jpeg, "image/jpeg")}
        response = self.client.post("/api/analyze/image", files=file_payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["filename"], "test_deepfake.jpg")
        self.assertIn("trust_score", data)
        self.assertIn("threat_level", data)
        self.assertIn("ela_image_base64", data)
        self.assertTrue(data["ela_image_base64"].startswith("data:image/png;base64,"))
        
        # Verify metadata present/missing arrays
        self.assertIn("metadata", data)
        self.assertIn("present_metadata", data["metadata"])
        self.assertIn("missing_metadata", data["metadata"])
        
        # Verify advanced forensics breakdown fields
        self.assertIn("forensics", data)
        self.assertIn("deepfake_probability", data["forensics"])
        self.assertIn("ela_anomaly_rating", data["forensics"])
        self.assertIn("avg_diff", data["forensics"])
        self.assertIn("max_diff", data["forensics"])
        self.assertIn("splicing_detected", data["forensics"])

    def test_url_scanning_apnews(self):
        payload = {"url": "apnews.com"}
        response = self.client.post("/api/analyze/url", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["domain"], "apnews.com")
        self.assertGreaterEqual(data["trust_score"], 80) # Trusted domain
        
        # Assert updated credibility scanner metadata keys
        self.assertIn("security", data)
        self.assertIn("redirects", data)
        self.assertIn("suspicious_keywords", data)
        self.assertIn("whois", data)
        self.assertIn("threat_level", data)
        self.assertTrue(data["security"]["is_https"])
        self.assertIn("domain_age_years", data["whois"])
        self.assertIn("registrar", data["whois"])
        self.assertIn("history", data["redirects"])
        self.assertIn("detected", data["suspicious_keywords"])

    def test_suspicious_url_credibility_low_score(self):
        # A highly suspicious URL with multiple negative indicators
        payload = {"url": "http://free-money-prize-claim-login.xyz"}
        response = self.client.post("/api/analyze/url", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["domain"], "free-money-prize-claim-login.xyz")
        
        # Must score well below 30
        self.assertLess(data["trust_score"], 30)
        self.assertEqual(data["threat_level"], "Critical / Phishing Risk")
        
        # Verify specific findings are triggered
        finding_titles = [f["title"] for f in data["findings"]]
        self.assertIn("Insecure HTTP Protocol", finding_titles)
        self.assertIn("Suspicious Top-Level Domain (TLD)", finding_titles)
        self.assertIn("Excessive Domain Hyphenation", finding_titles)
        self.assertIn("Phishing Lexicon Matched", finding_titles)

    def test_report_lifecycle(self):
        # 1. Create a report
        payload = {
            "title": "Unit Test Fake Claim Report",
            "description": "This is a fake claim used for verifying database insertions.",
            "category": "General News",
            "source_type": "Text",
            "source_reference": "Unit Test Script",
            "threat_level": "Suspicious",
            "trust_score": 45,
            "notes": "Verified automatically via TestClient."
        }
        create_res = self.client.post("/api/reports", json=payload)
        self.assertEqual(create_res.status_code, 200)
        create_data = create_res.json()
        self.assertTrue(create_data["success"])
        report_id = create_data["report"]["_id"]
        
        # 2. Get list of reports and verify our report is inside
        list_res = self.client.get("/api/reports")
        self.assertEqual(list_res.status_code, 200)
        list_data = list_res.json()
        self.assertTrue(list_data["success"])
        self.assertGreaterEqual(len(list_data["reports"]), 1)
        
        # Find our report in the registry list
        found = False
        for report in list_data["reports"]:
            if report["id"] == report_id or report.get("_id") == report_id:
                found = True
                self.assertEqual(report["title"], "Unit Test Fake Claim Report")
                break
        self.assertTrue(found)

        # 3. Update report status
        update_payload = {"status": "Investigated", "notes": "Completed manual verification"}
        update_res = self.client.put(f"/api/reports/{report_id}", json=update_payload)
        self.assertEqual(update_res.status_code, 200)

        # 4. Delete the report
        delete_res = self.client.delete(f"/api/reports/{report_id}")
        self.assertEqual(delete_res.status_code, 200)
        
        # 5. Verify it's gone
        list_res_after = self.client.get("/api/reports")
        reports_after = list_res_after.json()["reports"]
        ids = [r.get("id") or r.get("_id") for r in reports_after]
        self.assertNotIn(report_id, ids)

    def test_scam_message_predict(self):
        # 1. Test POST /predict with message key (expecting a scam text to be classified)
        payload1 = {"message": "URGENT! Your mobile number was awarded 2,000,000 pounds. Call 09066368727 to claim your prize."}
        response1 = self.client.post("/predict", json=payload1)
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()
        self.assertTrue(data1["success"])
        self.assertEqual(data1["prediction"], "scam")
        self.assertEqual(data1["prediction_label"], "scam")
        self.assertIn("confidence", data1)
        self.assertIn("confidence_score", data1)
        self.assertIn("threat_level", data1)
        self.assertEqual(data1["threat_level"], "Critical")
        self.assertIn("suspicious_keywords", data1)
        self.assertIn("urgent", data1["suspicious_keywords"])
        self.assertIn("probabilities", data1)

        # 2. Test POST /api/predict with text key (expecting a standard ham text)
        payload2 = {"text": "Hey, are we still meeting today?"}
        response2 = self.client.post("/api/predict", json=payload2)
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertTrue(data2["success"])
        self.assertEqual(data2["prediction"], "safe")
        self.assertEqual(data2["prediction_label"], "safe")
        self.assertIn("confidence_score", data2)
        self.assertIn("threat_level", data2)
        self.assertEqual(data2["threat_level"], "Safe")
        self.assertFalse(data2["is_scam"])

    def test_rag_search_faiss_and_qdrant(self):
        # Test FAISS
        faiss_payload = {"query": "COVID vaccines 5G tracking microchip", "top_k": 2, "engine": "faiss"}
        res_faiss = self.client.post("/api/rag/search", json=faiss_payload)
        self.assertEqual(res_faiss.status_code, 200)
        data_faiss = res_faiss.json()
        self.assertTrue(data_faiss["success"])
        self.assertGreaterEqual(len(data_faiss["documents"]), 1)
        self.assertIn("FAISS", data_faiss["documents"][0]["engine"])

        # Test Qdrant
        qdrant_payload = {"query": "COVID vaccines 5G tracking microchip", "top_k": 2, "engine": "qdrant"}
        res_qdrant = self.client.post("/api/rag/search", json=qdrant_payload)
        self.assertEqual(res_qdrant.status_code, 200)
        data_qdrant = res_qdrant.json()
        self.assertTrue(data_qdrant["success"])
        self.assertGreaterEqual(len(data_qdrant["documents"]), 1)
        self.assertIn("Qdrant", data_qdrant["documents"][0]["engine"])

    def test_rag_verify_with_ragas_and_deepeval(self):
        payload = {"claim": "Volcanoes emit far more CO2 than human industry.", "vector_engine": "faiss"}
        res = self.client.post("/api/rag/verify", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("FALSE", data["verdict"])
        self.assertIn("ragas_metrics", data)
        self.assertIn("faithfulness", data["ragas_metrics"])
        self.assertIn("answer_relevance", data["ragas_metrics"])
        self.assertIn("context_precision", data["ragas_metrics"])
        self.assertIn("context_recall", data["ragas_metrics"])
        self.assertIn("deepeval_metrics", data)
        self.assertIn("hallucination_metric", data["deepeval_metrics"])
        self.assertIn("contextual_relevancy", data["deepeval_metrics"])

    def test_rag_benchmark_endpoint(self):
        res = self.client.get("/api/rag/benchmark")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("benchmark_summary", data)
        self.assertGreater(data["benchmark_summary"]["mean_ragas_faithfulness"], 0.6)
        self.assertLess(data["benchmark_summary"]["mean_deepeval_hallucination_rate"], 0.4)

if __name__ == "__main__":
    unittest.main()

