from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests
import json
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Custom AI Assistant API",
    description="API for interacting with various AI models via AIHubMix",
    version="1.1.0"
)

# === CORS MIDDLEWARE ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AIHubMix Configuration
AIHUBMIX_URL = "https://aihubmix.com/v1/chat/completions"
API_KEY = "sk-swWOwPZXuCrUhrmD173c4d1b57A84038967c489eA52dA6F2"

AVAILABLE_MODELS = [
    "gemini-3.7-flash-free",
    "gemini-3.5-flash-lite-free",
    "gemini-3.6-flash-free",
    "coding-glm-5.2-free",
    "coding-kimi-k3-free",
    "gpt-oss-20b-free",
    "nemotron-3-ultra-550b-a55b-free",
    "coding-minimax-m3-free",
    "gpt-5.5-free",
    "gpt-image-2-free",
    "xiaomi-mimo-v2-pro-free",
    "coding-glm-5-turbo-free",
    "gemini-3.1-flash-image-preview-free",
    "gemini-3-flash-preview-free",
    "gpt-4.1-nano-free",
    "gpt-4.1-mini-free",
    "coding-glm-4.7-free",
    "k2.6-code-preview-free",
    "coding-minimax-m2-free",
    "google/gemma-2-9b-it:free"
]

class ChatRequest(BaseModel):
    message: str = Field(..., description="The prompt or question for the AI")
    model: str = Field(default="gemini-3.7-flash-free", description="The AI model to use")
    system_prompt: str = Field(default="You are a helpful AI assistant.", description="Instructions for AI behavior")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Creativity level")
    max_tokens: int = Field(default=1024, description="Maximum length of response")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome! Use /api?message=YourText to test quickly.",
        "models_endpoint": "Visit /api/models to see available models."
    }

@app.get("/api/models")
def get_models():
    return {"status": "success", "available_models": AVAILABLE_MODELS}

# =========================================================
# নতুন সিস্টেম: লিংকের মাধ্যমে সরাসরি প্রশ্ন করার জন্য (GET Request)
# =========================================================
@app.get("/api")
def quick_chat(message: str, model: str = "gemini-3.7-flash-free"):
    """
    লিংক থেকে সরাসরি প্রশ্ন করার জন্য। 
    উদাহরণ: /api?message=Hello
    """
    if model not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model '{model}'.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant. Answer in Bengali."},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        response = requests.post(AIHUBMIX_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        response_data = response.json()
        ai_reply = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        return {
            "question": message,
            "reply": ai_reply
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if response.text:
            error_msg += f" | Details: {response.text}"
        raise HTTPException(status_code=500, detail=f"API Error: {error_msg}")

# =========================================================
# ওয়েবসাইটের (চ্যাটবট) জন্য আগের সিস্টেম (POST Request)
# =========================================================
@app.post("/api/chat")
def generate_chat_response(request: ChatRequest):
    if request.model not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model '{request.model}'.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": request.model,
        "messages": [
            {"role": "system", "content": request.system_prompt},
            {"role": "user", "content": request.message}
        ],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens
    }

    try:
        response = requests.post(AIHUBMIX_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        response_data = response.json()
        ai_reply = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        return {
            "status": "success",
            "model_used": request.model,
            "reply": ai_reply
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if response.text:
            error_msg += f" | Details: {response.text}"
        raise HTTPException(status_code=500, detail=f"API Error: {error_msg}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
