from openai_client import get_openai_response
from pinecone_client import search_pinecone, store_conversation
from starlette.responses import StreamingResponse

async def stream_openai_response(query, session_id):
    """Streams OpenAI's response chunk by chunk while using Pinecone for context."""
    relevant_info = await search_pinecone(query)

    prompt = f"""You are a chatbot trained on personal data about Annie. Pretend you are Annie. Be friendly, personable, and professional.
            Focus on my full-stack experience.
           Don't make your responses too long, be very concise and clear. Don't ask the user any questions.
           Here is some background information:
           {relevant_info}

           Format your response as if you are talking to someone.

           Based on this, answer the following question:
           {query}"""

    response_stream = await get_openai_response(prompt)

    collected_response = ""

    async def event_stream():
        nonlocal collected_response
        async for chunk in response_stream:
            if chunk.choices and hasattr(chunk.choices[0].delta, "content"):
                text = chunk.choices[0].delta.content
                if text:
                    collected_response += text
                    yield f"{text}"
        await store_conversation(query, collected_response, session_id)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
