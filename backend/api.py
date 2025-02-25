from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from chatbot import stream_openai_response
import os
import uuid
from dotenv import load_dotenv
import sys


load_dotenv()

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.anniecaroline.com/"],  # Update this with Railway frontend URL after deployment
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

session_id = str(uuid.uuid4())

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    if not message:
        return {"error": "Message parameter is required"}
    return await stream_openai_response(message, session_id)

@app.get("/")
def home():
    return {"message": "Welcome to the chatbot API! Use /chat to interact."}

@app.get("/debug")
def debug():
    return {
        "env": dict(os.environ),
        "working_dir": os.getcwd(),
        "files": os.listdir("."),
        "pythonpath": sys.path
    }
