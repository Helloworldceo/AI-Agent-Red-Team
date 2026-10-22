from fastapi import APIRouter

from app.models.payload import TargetType
from app.payloads.registry import ALL_PAYLOADS, get_by_target_type

router = APIRouter()


@router.get("/payloads")
def list_payloads(target_type: TargetType | None = None):
    payloads = get_by_target_type(target_type) if target_type else ALL_PAYLOADS
    return {"payloads": [p.model_dump() for p in payloads]}


@router.get("/providers")
def list_providers():
    return {
        "providers": [
            {"id": "deepseek", "label": "DeepSeek", "default_model": "deepseek-chat"},
            {"id": "gemini", "label": "Gemini", "default_model": "gemini-2.0-flash"},
        ]
    }


@router.get("/targets")
def list_targets():
    return {
        "targets": [
            {
                "type": TargetType.DIRECT_CHAT,
                "label": "Direct Chat",
                "blurb": "A raw system prompt + LLM call. No tools, no retrieval.",
            },
            {
                "type": TargetType.TOOL_AGENT,
                "label": "Tool-Calling Agent",
                "blurb": "A LangGraph agent with mock tools of varying sensitivity — tests excessive agency.",
            },
            {
                "type": TargetType.RAG,
                "label": "RAG Assistant",
                "blurb": "A retrieval-augmented chat that drops retrieved documents into the system prompt — tests indirect injection via poisoned documents.",
            },
        ]
    }
