from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from chatbot import stream_openai_response
import os
import uuid
from dotenv import load_dotenv
import sys


load_dotenv()

app = FastAPI()
origins = ["http://localhost:3001", "http://localhost:5001", "https://www.anniecaroline.com"]
# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

session_id = str(uuid.uuid4())

@app.options("/chat")
async def chat_options():
    """Handle CORS preflight requests for /chat endpoint"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "600",
        }
    )

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
@app.post("/chat-simple")
async def chat_simple(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")
        if not message:
            return {"error": "Message parameter is required"}
        
        # Test basic functionality without streaming
        from chatbot import clarify_user_query, search_pinecone, summarize_context
        from openai_client import get_openai_chatcompletion_nonstream
        
        clarified = await clarify_user_query(message)
        joined_text, matches = await search_pinecone(clarified, top_k=3)
        curated = await summarize_context(clarified, joined_text)
        
        # Simple non-streaming response
        messages = [
            {"role": "system", "content": "You are Annie, a friendly developer. Keep responses concise."},
            {"role": "user", "content": f"Context: {curated}\n\nUser: {clarified}"}
        ]
        
        response = await get_openai_chatcompletion_nonstream(messages)
        return {"response": response}
        
    except Exception as e:
        return {"error": f"Error: {str(e)}"}