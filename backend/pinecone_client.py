import os
import time
import pinecone
from openai_client import get_query_embedding
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Load environment variables (ensure these are set in your .env and Railway environment)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Initialize the new Pinecone client
client = pinecone.Client(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

# Create the index if it doesn't exist
if PINECONE_INDEX_NAME not in client.list_indexes():
    client.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536,  # for OpenAI text-embedding-ada-002
        metric="cosine"
    )

# Get a reference to the index
index = client.Index(PINECONE_INDEX_NAME)

# Get a reference to your index
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


async def search_pinecone(query):
    query_embedding = await get_query_embedding(query)

    results = await asyncio.to_thread(
        index.query, vector=query_embedding, top_k=5, include_metadata=True
    )

    retrieved_texts = [match["metadata"].get("text", "No relevant text found.") for match in results["matches"]]
    print("\n Pinecone data: \n", retrieved_texts, "\n")
    return "\n".join(retrieved_texts)
