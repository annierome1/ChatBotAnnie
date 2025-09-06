import os
import time
from pinecone import Pinecone
from openai_client import get_query_embedding
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)


async def store_conversation(user_query, bot_response, session_id):
    """Stores chat history under a session ID in Pinecone."""
    query_embedding = await get_query_embedding(user_query)
    response_embedding = await get_query_embedding(bot_response)

    if not query_embedding or not response_embedding:
        print("Failed to generate embeddings. Skipping upsert.")
        return

    timestamp = time.time()

    try:
        index.upsert(
            vectors=[
                (f"{session_id}_query_{hash(user_query)}", query_embedding,
                 {"type": "session_chat", "session_id": session_id, "text": user_query, "paired_response": bot_response,
                  "timestamp": timestamp}),
                (f"{session_id}_response_{hash(bot_response)}", response_embedding,
                 {"type": "session_chat", "session_id": session_id, "text": bot_response, "paired_query": user_query,
                  "timestamp": timestamp})
            ],
            namespace="conversations"
        )
        print(f"Stored chat in session {session_id}!")

    except Exception as e:
        print(f"Error storing conversation in Pinecone: {e}")


def _build_filter(types=None, audience=None, project=None):
    f = {}
    if types:
        types = list(types)
        f["type"] = {"$eq": types[0]} if len(types) == 1 else {"$in": types}
    if audience:
        f["audience"] = {"$eq": audience}
    if project:
        f["project"] = {"$eq": project}
    return f or None

async def search_pinecone(
    query: str,
    top_k: int = 8,
    types: list[str] | None = None,
    audience: str | None = None,
    project: str | None = None,
    namespace: str = "public"
):
    """
    Vector search with optional metadata filtering.
    Returns both a joined text block and raw matches for debugging/reranking.
    """
    query_embedding = await get_query_embedding(query)

    pinecone_filter = _build_filter(types=types, audience=audience, project=project)

    results = await asyncio.to_thread(
        index.query,
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace,
        filter=pinecone_filter
    )

    matches = results.get("matches", []) or []
    retrieved = []
    for m in matches:
        md = m.get("metadata", {}) or {}
        retrieved.append({
            "id": m.get("id"),
            "score": m.get("score"),
            "type": md.get("type"),
            "project": md.get("project"),
            "audience": md.get("audience"),
            "text": md.get("text", "No relevant text found.")
        })

    # Keep your original behavior (return a big string), but also return matches for logging.
    joined_text = "\n".join(item["text"] for item in retrieved)
    # Helpful debug print to see *what* you got back:
    print("\n Pinecone matches (type, project, score, id):")
    for item in retrieved:
        print(f"  - {item['type']}, {item['project']}, {item['score']:.3f}, {item['id']}")
    print()
    return joined_text, retrieved
