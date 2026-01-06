import os
from typing import List

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "mindly-chairmans-council")
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")

COUNCIL_MODELS: List[str] = [
    "openai/gpt-4-turbo-preview",
    "anthropic/claude-3-opus",
    "google/gemini-2.0-flash",
]

CHAIRMAN_MODEL = "google/gemini-2.0-flash"

MAX_TOKENS_PER_RESPONSE = 2000
COUNCIL_TIMEOUT_SECONDS = 120
CHAIRMAN_TIMEOUT_SECONDS = 90

DOMAIN = "healthcare"
USE_HEALTHCARE_PROMPTS = True
CLINICAL_CONTEXT = True

LOG_LEVEL = "INFO"
ENABLE_COST_TRACKING = True

# Settings object for easy access
class Settings:
    openrouter_api_key = OPENROUTER_API_KEY
    openrouter_base_url = OPENROUTER_BASE_URL
    firebase_project_id = FIREBASE_PROJECT_ID
    firebase_credentials_path = FIREBASE_CREDENTIALS_PATH
    council_models = COUNCIL_MODELS
    chairman_model = CHAIRMAN_MODEL
    max_tokens_per_response = MAX_TOKENS_PER_RESPONSE
    council_timeout_seconds = COUNCIL_TIMEOUT_SECONDS
    chairman_timeout_seconds = CHAIRMAN_TIMEOUT_SECONDS
    domain = DOMAIN
    use_healthcare_prompts = USE_HEALTHCARE_PROMPTS
    clinical_context = CLINICAL_CONTEXT
    log_level = LOG_LEVEL
    enable_cost_tracking = ENABLE_COST_TRACKING

settings = Settings()
