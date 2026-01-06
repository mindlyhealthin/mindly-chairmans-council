from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Configuration for Chairman's Council"""
    
    # API Configuration
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: str
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"
    
    # Council Model Configuration
    COUNCIL_MODELS: List[str] = [
        "openai/gpt-4-turbo-preview",
        "anthropic/claude-3-opus",
        "google/gemini-2.0-flash",
    ]
    
    CHAIRMAN_MODEL: str = "google/gemini-2.0-flash"
    
    # Performance Settings
    MAX_TOKENS_PER_RESPONSE: int = 2000
    COUNCIL_TIMEOUT_SECONDS: int = 120
    CHAIRMAN_TIMEOUT_SECONDS: int = 90
    
    # Healthcare Domain Settings
    DOMAIN: str = "healthcare"
    USE_HEALTHCARE_PROMPTS: bool = True
    CLINICAL_CONTEXT: bool = True
    
    # Logging & Monitoring
    LOG_LEVEL: str = "INFO"
    ENABLE_COST_TRACKING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
