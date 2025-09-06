# chatbot.py
import logging
import time
from pinecone_client import store_conversation
from fastapi.responses import StreamingResponse
from openai_client import (
    get_openai_chatcompletion_nonstream,  # non-streaming
    stream_chat_with_messages             # <-- NEW: streaming with messages
)
from pinecone_client import search_pinecone

logging.basicConfig(level=logging.INFO)

VOICE_SYSTEM_PROMPT = (
    "You are Annie. Respond naturally using the context provided. "
    "Keep responses to 5-6 sentences maximum. "
    "If you have more to say, ask 'Should I keep going?' at the end. "
    "No links or email addresses. Use only facts from the provided context."
     "Never list things in bullet points or formal lists. Make it sound like a conversation."
)

GROUNDING_RULES = (
    "Use only the facts from the retrieved context. "
    "Answer in first person when talking about Annie. "
    "Keep responses to 5-6 sentences maximum. "
    "If you have more to say, end with 'Should I keep going?'"
    "Never list things in bullet points or formal lists. Make it sound like a conversation."
)
def _route_types(clarified: str) -> list[str] | None:
    q = clarified.lower()
    # Route common intents to metadata types
    if any(w in q for w in ["project", "portfolio", "built", "site", "app", "extension"]):
        return ["project"]
    if any(w in q for w in ["who are you", "about you", "bio", "background"]):
        return ["voice_profile", "bio", "qa_persona", "pitch"]
    if any(w in q for w in ["email", "dm", "message", "reach out", "referral"]):
        return ["comms_samples", "style_pair"]
    # default: no filter
    return None

async def clarify_user_query(original_query: str) -> str:
    # (unchanged)
    messages = [
        {"role": "system", "content": "You are a helpful AI that restates user questions."},
        {"role": "user", "content": f"Please restate or clarify the following query: {original_query}"}
    ]
    clarified = await get_openai_chatcompletion_nonstream(messages)
    return clarified.strip()

async def summarize_context(clarified_query: str, pinecone_results: str) -> str:
    # (unchanged but with slightly stronger instruction)
    messages = [
        {"role": "system", "content": "You are an expert summarizer."},
        {"role": "user", "content":
            f"User Query (clarified): {clarified_query}\n\n"
            f"Context from Pinecone:\n{pinecone_results}\n\n"
            "If the query is about Annie generally, emphasize voice/bio/QA."}
    ]
    summary = await get_openai_chatcompletion_nonstream(messages)
    return summary.strip()

async def stream_openai_response(query, session_id):
    try:
        clarified = await clarify_user_query(query)

        # ROUTE: ask Pinecone for the right types first
        desired_types = _route_types(clarified)
        joined_text, matches = await search_pinecone(
            clarified,
            top_k=8,
            types=desired_types  # <= key change: filter by type when we can
        )

        # If filtering came back too thin, do a small backfill without filter
        if len(matches) < 2 and desired_types:
            extra_text, extra_matches = await search_pinecone(clarified, top_k=6, types=None)
            joined_text = (joined_text + "\n" + extra_text).strip()
            matches += extra_matches

        curated = await summarize_context(clarified, joined_text)

        messages = [
            {"role": "system", "content": VOICE_SYSTEM_PROMPT},
            {"role": "system", "content": GROUNDING_RULES},
            {"role": "system", "content": f"Context (summarized):\n{curated}"},
            {"role": "user", "content": clarified}
        ]

        response_stream = await stream_chat_with_messages(messages)
        collected_response = ""

        async def event_stream():
            nonlocal collected_response
            try:
                async for chunk in response_stream:
                    if chunk.choices and hasattr(chunk.choices[0].delta, "content"):
                        text = chunk.choices[0].delta.content
                        if text:
                            collected_response += text
                            yield text
            except Exception as e:
                logging.error(f"Error during response streaming: {e}")
                yield f"\nError during response streaming: {e}"

            # Save conversation (unchanged; stored under namespace='conversations')
            try:
                start_time = time.time()
                await store_conversation(query, collected_response, session_id)
                logging.info(f"Time taken to store convo: {time.time() - start_time:.4f} seconds.")
            except Exception as e:
                logging.error(f"Error storing conversation: {e}")

        logging.info("Starting to stream response to client.")
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        logging.error(f"Error in stream_openai_response: {e}")
        async def error_stream():
            yield f"Error: {e}"
        return StreamingResponse(error_stream(), media_type="text/event-stream")