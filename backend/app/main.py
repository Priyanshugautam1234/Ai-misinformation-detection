from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import logging
import os
import joblib

from .config import settings
from .database import get_db_status
from .nlp_models import analyzer as nlp_analyzer
from .image_detection import detector as img_detector
from .url_analysis import scanner as url_scanner
from .reporting_system import manager as report_manager

# Init Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load scikit-learn models from app/models
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
model_path = os.path.join(MODELS_DIR, "spam_model.pkl")
vectorizer_path = os.path.join(MODELS_DIR, "vectorizer.pkl")

try:
    logger.info(f"Loading scam detection model from {model_path}...")
    spam_model = joblib.load(model_path)
    logger.info("Scam detection model loaded successfully!")
    
    logger.info(f"Loading TF-IDF vectorizer from {vectorizer_path}...")
    vectorizer = joblib.load(vectorizer_path)
    logger.info("Vectorizer loaded successfully!")
except Exception as e:
    logger.error(f"Failed to load ML models: {e}")
    spam_model = None
    vectorizer = None

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-stack AI engine evaluating text claims, digital image forensics, and URL reputation.",
    version="1.0.0"
)

# CORS Policy configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow access from the Vite React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class TextAnalysisRequest(BaseModel):
    text: str

class UrlAnalysisRequest(BaseModel):
    url: str

class PredictRequest(BaseModel):
    message: Optional[str] = None
    text: Optional[str] = None

class ReportCreateRequest(BaseModel):
    title: str
    description: str
    category: str
    source_type: str
    source_reference: str
    threat_level: str
    trust_score: int
    notes: Optional[str] = ""

class StatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None

# 1. Base endpoints
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the AI Misinformation Detection Platform API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/api/status")
def get_system_status():
    db_status = get_db_status()
    return {
        "status": "healthy",
        "database": db_status,
        "modules": {
            "nlp_analyzer": "operational",
            "image_forensics": "operational",
            "url_reputation_crawler": "operational"
        }
    }

# 2. Analysis Endpoints
@app.post("/api/analyze/text")
def analyze_claim_text(request: TextAnalysisRequest):
    result = nlp_analyzer.analyze_text(request.text)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/api/analyze/image")
async def analyze_claim_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        result = img_detector.analyze_image(content, file.filename)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Image parsing failed: {str(e)}")

@app.post("/api/analyze/url")
async def analyze_claim_url(request: UrlAnalysisRequest):
    result = await url_scanner.scan_url(request.url)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/predict")
@app.post("/api/predict")
def predict_scam_message(request: PredictRequest):
    content = request.message or request.text
    if not content:
        raise HTTPException(status_code=400, detail="Either 'message' or 'text' must be provided in request body.")
        
    if spam_model is None or vectorizer is None:
        raise HTTPException(status_code=503, detail="ML classification models are currently unavailable.")
        
    try:
        # Transform and Predict
        X_vec = vectorizer.transform([content])
        prediction = spam_model.predict(X_vec)[0]
        
        # 0 is safe/ham, 1 is spam/scam (standard convention)
        is_scam = bool(prediction == 1)
        label = "scam" if is_scam else "safe"
        
        confidence = 0.5
        probabilities = None
        if hasattr(spam_model, "predict_proba"):
            probs = spam_model.predict_proba(X_vec)[0]
            confidence = float(max(probs))
            probabilities = {
                "safe": float(probs[0]),
                "scam": float(probs[1])
            }
            
        # Determine threat level based on prediction and confidence
        if is_scam:
            threat_level = "Critical" if confidence >= 0.8 else "Suspicious"
        else:
            threat_level = "Safe" if confidence >= 0.7 else "Suspicious"

        # Detect suspicious keywords case-insensitively
        suspicious_terms = ["urgent", "click now", "winner", "blocked", "otp", "free", "bank"]
        detected_keywords = [term for term in suspicious_terms if term in content.lower()]

        return {
            "success": True,
            "message": content,
            "prediction": label,
            "prediction_label": label,
            "is_scam": is_scam,
            "confidence": round(confidence, 4),
            "confidence_score": round(confidence, 4),
            "threat_level": threat_level,
            "suspicious_keywords": detected_keywords,
            "probabilities": probabilities
        }
    except Exception as e:
        logger.error(f"Prediction inference error: {e}")
        raise HTTPException(status_code=500, detail=f"Inference computation failed: {str(e)}")

# 3. User Reports Endpoints
@app.post("/api/reports")
def submit_new_report(request: ReportCreateRequest):
    try:
        report = report_manager.create_report(request.model_dump())
        return {
            "success": True,
            "message": "Report registered in AI catalog.",
            "report": report
        }
    except Exception as e:
        logger.error(f"Report submission failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports")
def fetch_all_reports(
    category: Optional[str] = Query("All"),
    source_type: Optional[str] = Query("All"),
    search: Optional[str] = Query(None)
):
    try:
        reports = report_manager.list_reports(category, source_type, search)
        return {
            "success": True,
            "count": len(reports),
            "reports": reports
        }
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/reports/{report_id}")
def update_report(report_id: str, request: StatusUpdateRequest):
    success = report_manager.update_report_status(report_id, request.status, request.notes)
    if not success:
        raise HTTPException(status_code=404, detail="Report ID not found or not modified.")
    return {"success": True, "message": "Report status updated."}

@app.delete("/api/reports/{report_id}")
def remove_report(report_id: str):
    success = report_manager.delete_report(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report ID not found in database.")
    return {"success": True, "message": "Report removed successfully from database."}

@app.get("/api/reports/analytics")
def fetch_system_analytics():
    try:
        analytics = report_manager.get_report_analytics()
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        logger.error(f"Analytics computation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
