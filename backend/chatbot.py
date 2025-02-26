# chatbot.py
import logging
import time
from pinecone_client import store_conversation
from fastapi.responses import StreamingResponse
from openai_client import (
    get_openai_response,               # streaming
    get_openai_chatcompletion_nonstream  # non-streaming
)
from pinecone_client import search_pinecone

logging.basicConfig(level=logging.INFO)

async def clarify_user_query(original_query: str) -> str:
    """
    Makes a quick, non-streaming call to restate or clarify the user's query.
    """
    start_time = time.time()
    messages = [
        {"role": "system", "content": "You are a helpful AI that restates user questions."},
        {"role": "user", "content": f"Please restate or clarify the following query: {original_query}"}
    ]
    clarified = await get_openai_chatcompletion_nonstream(messages)
    end_time = time.time()
    logging.info(f"Query clarification took {end_time - start_time: .4f} seconds.")
    return clarified.strip()

async def summarize_context(clarified_query: str, pinecone_results: str) -> str:
    """
    Makes a quick, non-streaming call to summarize the Pinecone context
    so the final prompt can be concise.
    """
    start_time = time.time()
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
    end_time = time.time()
    logging.info(f"Context summarization: {end_time - start_time:.4f} seconds.")
    return summary.strip()


async def stream_openai_response(query, session_id):

    # Step 1: Clarify query
    start_time = time.time()
    clarified_query = await clarify_user_query(query)
    end_time = time.time()
    logging.info(f"Total time for query clarification: {end_time - start_time:.4f} seconds.")

    # Step 2: Search Pinecone for relevant info
    start_time = time.time()
    pinecone_info = await search_pinecone(clarified_query)
    end_time = time.time()
    logging.info(f"Pinecone search took: {end_time - start_time:.4f} seconds.")


    # Step 3: Summarize the retrieved info
    start_time = time.time()
    summary = await summarize_context(clarified_query, pinecone_info)
    end_time = time.time()
    logging.info(f"otal time for summarization: {end_time - start_time:.4f} seconds.")

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
    start_time = time.time()
    response_stream = await get_openai_response(final_prompt)
    end_time = time.time()
    logging.info(f"Time taken to start OpenAI response streaming: {end_time - start_time:.4f} seconds.")
    collected_response = ""

    async def event_stream():
        nonlocal collected_response
        async for chunk in response_stream:
            if chunk.choices and hasattr(chunk.choices[0].delta, "content"):
                text = chunk.choices[0].delta.content
                if text:
                    collected_response += text
                    yield text

        # After streaming is done, store the conversation
        start_time = time.time()
        await store_conversation(query, collected_response, session_id)
        end_time = time.time()
        logging.info(f"Time taken to store convo: {end_time - start_time:.4f} seconds.")

    end_time = time.time()
    logging.info(f"Total request processing time: {end_time - start_time:.4f} seconds.")
    return StreamingResponse(event_stream(), media_type="text/event-stream")
