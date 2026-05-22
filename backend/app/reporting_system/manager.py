from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from ..database import get_db

db = get_db()
REPORTS_COLLECTION = "user_reports"

def create_report(report_data: Dict[str, Any]) -> Dict[str, Any]:
    collection = db[REPORTS_COLLECTION]
    
    # Structure the database report document
    report_doc = {
        "_id": str(uuid.uuid4()),
        "title": report_data.get("title", "Untitled Report"),
        "description": report_data.get("description", ""),
        "category": report_data.get("category", "General"),
        "source_type": report_data.get("source_type", "Text"), # Text, Image, URL
        "source_reference": report_data.get("source_reference", ""),
        "threat_level": report_data.get("threat_level", "Suspicious"), # Critical, Suspicious, Safe
        "trust_score": report_data.get("trust_score", 50),
        "status": "Pending Review", # Pending Review, Investigated, Resolved
        "timestamp": datetime.utcnow().isoformat(),
        "notes": report_data.get("notes", "")
    }
    
    result = collection.insert_one(report_doc)
    report_doc["id"] = result.inserted_id
    return report_doc

def list_reports(
    category: Optional[str] = None, 
    source_type: Optional[str] = None,
    search_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    collection = db[REPORTS_COLLECTION]
    
    filter_dict = {}
    if category and category != "All":
        filter_dict["category"] = category
    if source_type and source_type != "All":
        filter_dict["source_type"] = source_type
        
    reports = collection.find(filter_dict)
    
    # Handle search filter programmatically (since the mock collection does not support complex text indexes)
    if search_query:
        q = search_query.lower()
        filtered = []
        for r in reports:
            title_match = q in r.get("title", "").lower()
            desc_match = q in r.get("description", "").lower()
            ref_match = q in r.get("source_reference", "").lower()
            if title_match or desc_match or ref_match:
                filtered.append(r)
        reports = filtered
        
    # Sort reports by timestamp descending (newest first)
    # Convert _id to id for client convenience
    formatted_reports = []
    for r in reports:
        doc = dict(r)
        doc["id"] = str(doc.get("_id"))
        formatted_reports.append(doc)
        
    formatted_reports.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return formatted_reports

def delete_report(report_id: str) -> bool:
    collection = db[REPORTS_COLLECTION]
    result = collection.delete_one({"_id": report_id})
    return result.deleted_count > 0

def update_report_status(report_id: str, status: str, notes: Optional[str] = None) -> bool:
    collection = db[REPORTS_COLLECTION]
    update_data = {"status": status}
    if notes is not None:
        update_data["notes"] = notes
        
    result = collection.update_one({"_id": report_id}, {"$set": update_data})
    return result.modified_count > 0

def get_report_analytics() -> Dict[str, Any]:
    collection = db[REPORTS_COLLECTION]
    reports = collection.find()
    
    total = len(reports)
    
    # Categorization counts
    categories = {}
    threat_levels = {"Critical": 0, "Suspicious": 0, "Safe": 0}
    source_types = {"Text": 0, "Image": 0, "URL": 0}
    
    for r in reports:
        cat = r.get("category", "General")
        categories[cat] = categories.get(cat, 0) + 1
        
        thr = r.get("threat_level", "Suspicious")
        if thr in threat_levels:
            threat_levels[thr] += 1
            
        src = r.get("source_type", "Text")
        if src in source_types:
            source_types[src] += 1
            
    # Include some dummy/mock reports if the database is brand new, so the dashboard looks beautiful right away!
    if total == 0:
        # Prepopulate with 3 demo reports
        demo_reports = [
            {
                "title": "COVID-19 5G Vaccine Conspiracy",
                "description": "Viral WhatsApp chain claiming that new vaccine rollout contains 5G tracking microchips.",
                "category": "Health & Medical",
                "source_type": "Text",
                "source_reference": "WhatsApp Forward",
                "threat_level": "Critical",
                "trust_score": 12,
                "status": "Investigated",
                "notes": "Verified FALSE. Backed by extensive laboratory tests globally.",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "title": "Unverified Volcanic Emissions Claim",
                "description": "Claim stating volcano eruptions emit more carbon than humans.",
                "category": "Environment",
                "source_type": "URL",
                "source_reference": "https://beforeitsnews.com/post/volcano-emissions",
                "threat_level": "Suspicious",
                "trust_score": 35,
                "status": "Pending Review",
                "notes": "Flagged clickbait score. USGS lists volcanic emissions as < 1% of human emissions.",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "title": "Deepfake Politician Statement",
                "description": "Video of prime minister stating bank accounts will be closed this Friday.",
                "category": "Politics",
                "source_type": "Image",
                "source_reference": "politician_speech_face_swap.jpg",
                "threat_level": "Critical",
                "trust_score": 8,
                "status": "Resolved",
                "notes": "Facial landmark jitter and audio synthesis artifacts confirm deepfake.",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        for demo in demo_reports:
            create_report(demo)
            
        # Re-fetch populated mock database
        reports = collection.find()
        total = len(reports)
        categories = {}
        threat_levels = {"Critical": 0, "Suspicious": 0, "Safe": 0}
        source_types = {"Text": 0, "Image": 0, "URL": 0}
        for r in reports:
            cat = r.get("category", "General")
            categories[cat] = categories.get(cat, 0) + 1
            thr = r.get("threat_level", "Suspicious")
            if thr in threat_levels:
                threat_levels[thr] += 1
            src = r.get("source_type", "Text")
            if src in source_types:
                source_types[src] += 1
                
    # Return formatted details
    return {
        "total_reports": total,
        "categories": categories,
        "threat_levels": threat_levels,
        "source_types": source_types,
        "average_trust_score": round(sum(r.get("trust_score", 50) for r in reports) / total, 1) if total > 0 else 50
    }
