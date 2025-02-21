import os
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


async def get_query_embedding(query):
    """Generates embeddings for a given text query."""
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding


async def get_openai_response(prompt):
    """Calls OpenAI API for chat completion."""
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

    response_stream = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful AI assistant."},
                  {"role": "user", "content": prompt}],
        stream=True
    )
    return response_stream
