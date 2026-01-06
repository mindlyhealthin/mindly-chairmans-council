import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
from config import settings
from healthcare_prompts import (
    CLINICAL_ADVISOR_SYSTEM_PROMPT,
    PATIENT_ADVOCATE_SYSTEM_PROMPT,
    BUSINESS_STRATEGIST_SYSTEM_PROMPT,
    INNOVATION_LEAD_SYSTEM_PROMPT,
    CHAIRMAN_SYNTHESIS_PROMPT,
)
import json
from typing import Dict, List
import uuid
from datetime import datetime

load_dotenv()

app = FastAPI(
    title="Mindly Chairman's Council",
    description="Multi-model AI advisory council for Mindly Health",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Council member configurations
COUNCIL_MEMBERS = {
    "clinical_expert": {
        "model": "anthropic/claude-3-opus",
        "role": "Clinical Advisor",
        "prompt": CLINICAL_ADVISOR_SYSTEM_PROMPT,
    },
    "patient_advocate": {
        "model": "openai/gpt-4-turbo-preview",
        "role": "Patient Experience Advisor",
        "prompt": PATIENT_ADVOCATE_SYSTEM_PROMPT,
    },
    "business_strategist": {
        "model": "google/gemini-2.0-flash",
        "role": "Business & Operations Advisor",
        "prompt": BUSINESS_STRATEGIST_SYSTEM_PROMPT,
    },
    "innovation_lead": {
        "model": "meta-llama/llama-3-70b-instruct",
        "role": "Innovation & Technology Advisor",
        "prompt": INNOVATION_LEAD_SYSTEM_PROMPT,
    },
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Mindly Chairman's Council",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/council/query")
async def council_query(request: Dict):
    """Query the council for advice"""
    session_id = str(uuid.uuid4())
    query = request.get("query", "")
    
    if not query:
        return {"error": "Query is required"},  400
    
    # Stage 1: Get responses from all council members
    opinions = {}
    async with httpx.AsyncClient() as client:
        for member_id, member_config in COUNCIL_MEMBERS.items():
            try:
                response = await call_openrouter(
                    client=client,
                    model=member_config["model"],
                    system_prompt=member_config["prompt"],
                    user_message=query,
                )
                opinions[member_id] = {
                    "role": member_config["role"],
                    "model": member_config["model"],
                    "response": response,
                }
            except Exception as e:
                opinions[member_id] = {
                    "role": member_config["role"],
                    "error": str(e),
                }
    
    return {
        "session_id": session_id,
        "query": query,
        "stage": "stage_1_complete",
        "council_opinions": opinions,
        "timestamp": datetime.utcnow().isoformat(),
    }

async def call_openrouter(client: httpx.AsyncClient, model: str, system_prompt: str, user_message: str):
    """Call OpenRouter API"""
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://mindlyhealth.io",
        "X-Title": "Mindly Chairman's Council",
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": settings.MAX_TOKENS_PER_RESPONSE,
    }
    
    response = await client.post(
        f"{settings.OPENROUTER_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=settings.COUNCIL_TIMEOUT_SECONDS,
    )
    
    if response.status_code != 200:
        raise Exception(f"OpenRouter error: {response.text}")
    
    result = response.json()
    return result["choices"][0]["message"]["content"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
