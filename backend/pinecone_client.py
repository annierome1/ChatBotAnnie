import os
import time
import asyncio
from dotenv import load_dotenv
from pinecone import (
    Pinecone,
    ServerlessSpec,
    CloudProvider,
    AwsRegion,
    VectorType
)
from openai_client import get_query_embedding  # Your async function to get embeddings

load_dotenv()

# Load environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

# Create the index if it doesn't exist
pc = Pinecone(api_key='YOUR_API_KEY')

# 2. Create an index
index_config = pc.create_index(
    name="index-name",
    dimension=1536,
    spec=ServerlessSpec(
        cloud=CloudProvider.AWS,
        region=AwsRegion.US_EAST_1
    ),
    vector_type=VectorType.DENSE
)

# 3. Instantiate an Index client
idx = pc.Index(host=index_config.host)

async def store_conversation(user_query, bot_response, session_id):
    """Stores chat history under a session ID in Pinecone."""
    query_embedding = await get_query_embedding(user_query)
    response_embedding = await get_query_embedding(bot_response)

    if not query_embedding or not response_embedding:
        print("Failed to generate embeddings. Skipping upsert.")
        return

    timestamp = time.time()

    try:
        upsert_response = index.upsert(
            vectors=[
                (
                    f"{session_id}_query_{str(hash(user_query))}",
                    query_embedding,
                    {
                        "type": "session_chat",
                        "session_id": session_id,
                        "text": user_query,
                        "paired_response": bot_response,
                        "timestamp": timestamp
                    }
                ),
                (
                    f"{session_id}_response_{str(hash(bot_response))}",
                    response_embedding,
                    {
                        "type": "session_chat",
                        "session_id": session_id,
                        "text": bot_response,
                        "paired_query": user_query,
                        "timestamp": timestamp
                    }
                )
            ],
            namespace="conversations"
        )
        print(f"Stored chat in session {session_id}!")
        print(f"Upsert Response: {upsert_response}")
    except Exception as e:
        print(f"Error storing conversation in Pinecone: {e}")

async def search_pinecone(query):
    """Retrieves relevant information from Pinecone."""
    query_embedding = await get_query_embedding(query)

    results = await asyncio.to_thread(
        index.query, vector=query_embedding, top_k=5, include_metadata=True
    )

    retrieved_texts = [match["metadata"].get("text", "No relevant text found.") for match in results["matches"]]
    print("\nPinecone data:\n", retrieved_texts, "\n")
    return "\n".join(retrieved_texts)

