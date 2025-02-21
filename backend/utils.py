import time
import uuid

def generate_session_id():
    return str(uuid.uuid4())

def get_current_timestamp():
    return time.time()

def clean_streamed_response(chunk):
    return chunk.strip().replace("data:", "").strip()
