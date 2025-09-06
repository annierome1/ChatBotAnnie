import json
import asyncio
import time
from openai_client import get_query_embedding
from pinecone_client import index  # already initialized in your code

NAMESPACE = "public"  # your chatbot searches this namespace

async def upsert_jsonl(path):
    vectors = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            text = obj["text"]
            vec_id = obj["id"]
            metadata = obj.get("metadata", {})
            # include raw text in metadata for retrieval
            metadata["text"] = text  

            embedding = await get_query_embedding(text)
            vectors.append((vec_id, embedding, metadata))

    # Batch upsert (to avoid hitting request size limits, chunk if needed)
    print(f"Upserting {len(vectors)} vectors into Pinecone...")
    start = time.time()
    index.upsert(vectors=vectors, namespace=NAMESPACE)
    print(f"✅ Done in {time.time() - start:.2f}s.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ingest_jsonl.py /path/to/your_data.jsonl")
        sys.exit(1)
    asyncio.run(upsert_jsonl(sys.argv[1]))
