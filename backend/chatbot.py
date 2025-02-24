# chatbot.py
from pinecone_client import store_conversation
from fastapi.responses import StreamingResponse
from openai_client import (
    get_openai_response,               # streaming
    get_openai_chatcompletion_nonstream  # non-streaming
)
from pinecone_client import search_pinecone  # or wherever you keep this
# Also import or define store_conversation(...) if you have it

async def clarify_user_query(original_query: str) -> str:
    """
    Makes a quick, non-streaming call to restate or clarify the user's query.
    """
    messages = [
        {"role": "system", "content": "You are a helpful AI that restates user questions."},
        {"role": "user", "content": f"Please restate or clarify the following query: {original_query}"}
    ]
    clarified = await get_openai_chatcompletion_nonstream(messages)
    return clarified.strip()

async def summarize_context(clarified_query: str, pinecone_results: str) -> str:
    """
    Makes a quick, non-streaming call to summarize the Pinecone context
    so the final prompt can be concise.
    """
    messages = [
        {"role": "system", "content": "You are an expert summarizer."},
        {
            "role": "user",
            "content": (
                f"User Query (clarified): {clarified_query}\n\n"
                f"Context from Pinecone:\n{pinecone_results}\n\n"
                "Provide a concise summary or bullet points relevant to answering the query."
            )
        }
    ]
    summary = await get_openai_chatcompletion_nonstream(messages)
    return summary.strip()
# chatbot.py (continued)

async def stream_openai_response(query, session_id):
    """
    Streams OpenAI's response chunk by chunk using a tiered approach:
      1) Clarify the user query (quick non-streaming).
      2) Retrieve from Pinecone using clarified query.
      3) Summarize the Pinecone results (quick non-streaming).
      4) Stream final answer with condensed context.
    """
    # Step 1: Clarify query
    clarified_query = await clarify_user_query(query)

    # Step 2: Search Pinecone for relevant info
    pinecone_info = await search_pinecone(clarified_query)
    # pinecone_info is presumably a string or joined chunks

    # Step 3: Summarize the retrieved info
    summary = await summarize_context(clarified_query, pinecone_info)

    # Step 4: Build final prompt and stream the final answer
    final_prompt = f"""
    You are a chatbot trained on personal and professional information about Annie. Respond to questions as if you are Annie. Focus on her work as an aspiring full-stack developer.
    - For technical questions: provide clear, concise explanations and include brief examples or analogies if needed.
    - For general questions: keep your response high-level and engaging.
    Ensure your response is clear, contains no more than 4 sentences. Make sound personable, as if someone is actually talking to a young professional in their early 20s. Avoid slang, filler content, and do not include any email addresses or website links.
    
    Background summary:
    {summary}
    
    User query:
    {query}
    """

    # Use your existing streaming call:
    response_stream = await get_openai_response(final_prompt)

    collected_response = ""

    async def event_stream():
        nonlocal collected_response
        async for chunk in response_stream:
            if chunk.choices and hasattr(chunk.choices[0].delta, "content"):
                text = chunk.choices[0].delta.content
                if text:
                    collected_response += text
                    yield text  # stream to the user as soon as we get it

        # After streaming is done, store the conversation
        await store_conversation(query, collected_response, session_id)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
