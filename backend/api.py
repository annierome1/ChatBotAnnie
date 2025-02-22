from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from chatbot import stream_openai_response
import os
import uuid



app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Update this with Railway frontend URL after deployment
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
