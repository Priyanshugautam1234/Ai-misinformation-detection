import os

class Settings:
    PROJECT_NAME: str = "AI Misinformation Detection Platform"
    API_V1_STR: str = "/api"
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = "misinfo_db"
    
    # Port configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000

settings = Settings()
