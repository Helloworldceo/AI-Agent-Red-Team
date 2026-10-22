import os

from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TEMPERATURE = 0.0  # Deterministic responses for consistent scanning
REQUEST_TIMEOUT = 30  # Seconds before a request is considered timed out

# Google retires Gemini model IDs over time (gemini-2.0-flash was fully
# sunset, not just soft-deprecated) — if this 404s, check
# https://ai.google.dev/gemini-api/docs/models for the current recommended
# ID. Deliberately NOT using the "-latest" alias: Google documents it as a
# moving target that gets repointed to different model generations, which
# trades one kind of breakage for another.
GEMINI_DEFAULT_MODEL = "gemini-3.8-flash"

CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def get_api_key() -> str:
    """Local-dev convenience only — prefills the frontend's DeepSeek API key
    field. The key actually used for a scan always travels per-request,
    never read from here on the server side."""
    return os.getenv("DEEPSEEK_API_KEY", "")


def get_gemini_api_key() -> str:
    """Same local-dev convenience as get_api_key(), for Gemini."""
    return os.getenv("GEMINI_API_KEY", "")
