import os
import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def get_query_embedding(query):
    """Generates embeddings for a given text query."""
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
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

async def get_openai_chatcompletion_nonstream(messages, model="gpt-4"):
    """
    Calls OpenAI's ChatCompletion endpoint WITHOUT streaming,
    returning the full response as a string.
    """
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=False
    )
    return response.choices[0].message.content

# openai_client.py

async def stream_chat_with_messages(messages, model="gpt-4"):
    """
    Streaming chat completion that accepts full message arrays,
    so we can anchor a custom system prompt.
    """
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    return await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )
