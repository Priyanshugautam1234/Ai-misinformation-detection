import pymongo
from pymongo.errors import ServerSelectionTimeoutError
import logging
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory mock for MongoDB collections when MongoDB is unavailable
class MockCollection:
    def __init__(self, name: str):
        self.name = name
        self._data: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Initialized Mock MongoDB Collection: {name}")

    def insert_one(self, document: Dict[str, Any]) -> Any:
        doc = dict(document)
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        
        # Ensure _id is a string for easy matching
        _id = str(doc["_id"])
        self._data[_id] = doc
        
        class InsertOneResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        
        return InsertOneResult(_id)

    def find(self, filter_query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = list(self._data.values())
        if not filter_query:
            return results
        
        filtered = []
        for doc in results:
            match = True
            for k, v in filter_query.items():
                # Basic matching (equality)
                if k not in doc or doc[k] != v:
                    match = False
                    break
            if match:
                filtered.append(doc)
        return filtered

    def find_one(self, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        results = self.find(filter_query)
        return results[0] if results else None

    def update_one(self, filter_query: Dict[str, Any], update_query: Dict[str, Any]) -> Any:
        doc = self.find_one(filter_query)
        if not doc:
            class UpdateResult:
                def __init__(self):
                    self.modified_count = 0
            return UpdateResult()
        
        _id = str(doc["_id"])
        if "$set" in update_query:
            for k, v in update_query["$set"].items():
                self._data[_id][k] = v
        
        class UpdateResult:
            def __init__(self):
                self.modified_count = 1
        return UpdateResult()

    def delete_one(self, filter_query: Dict[str, Any]) -> Any:
        doc = self.find_one(filter_query)
        if not doc:
            class DeleteResult:
                def __init__(self):
                    self.deleted_count = 0
            return DeleteResult()
        
        _id = str(doc["_id"])
        del self._data[_id]
        
        class DeleteResult:
            def __init__(self):
                self.deleted_count = 1
        return DeleteResult()

    def count_documents(self, filter_query: Optional[Dict[str, Any]] = None) -> int:
        return len(self.find(filter_query))

class MockDatabase:
    def __init__(self):
        self._collections: Dict[str, MockCollection] = {}

    def __getitem__(self, name: str) -> MockCollection:
        if name not in self._collections:
            self._collections[name] = MockCollection(name)
        return self._collections[name]

# Global database client and db instances
db_client = None
db = None
is_mock = False

try:
    logger.info(f"Attempting to connect to MongoDB at {settings.MONGODB_URL}...")
    # 2 second server selection timeout so it fails quickly if down
    db_client = pymongo.MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
    # Trigger a command to check if server is reachable
    db_client.admin.command('ping')
    db = db_client[settings.DATABASE_NAME]
    is_mock = False
    logger.info("Successfully connected to live MongoDB database!")
except (ServerSelectionTimeoutError, Exception) as e:
    logger.warning(f"MongoDB connection failed: {e}")
    logger.warning("FALLING BACK TO IN-MEMORY MOCK DATABASE (All operations will work, but won't persist across restarts!)")
    db = MockDatabase()
    is_mock = True

def get_db():
    return db

def get_db_status() -> Dict[str, Any]:
    return {
        "status": "connected" if not is_mock else "mock_active",
        "type": "MongoDB Real" if not is_mock else "In-Memory Fallback",
        "database": settings.DATABASE_NAME,
        "url": settings.MONGODB_URL if not is_mock else "in-memory"
    }
