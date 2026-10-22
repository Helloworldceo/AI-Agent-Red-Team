from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.models.payload import PayloadKind, TargetType
from app.models.trace import TurnRecord

Severity = Literal["info", "low", "medium", "high", "critical"]


class ScanRequest(BaseModel):
    target_type: TargetType
    system_prompt: str
    goal: str
    api_key: str
    provider: Literal["deepseek", "gemini"] = "deepseek"
    model: str = "deepseek-chat"
    selected_payload_ids: list[str] | None = None
    eval_mode: Literal["keyword", "llm_judge"] = "llm_judge"


class ScanResultItem(BaseModel):
    id: str
    category: str
    name: str
    description: str
    kind: PayloadKind
    is_control: bool

    turns: list[TurnRecord]
    final_response: str
    retrieved_documents: list[dict] | None = None

    success: bool
    confidence: Literal["high", "medium", "low"]
    severity: Severity
    reason: str
    triggered_tools: list[str] = []

    error: str | None = None
    duration_ms: int


class ScanSummary(BaseModel):
    total: int
    succeeded: int
    failed: int
    errors: int
    success_rate: float
    by_category: dict[str, dict]
    by_severity: dict[str, int]
    risk_label: str
    risk_level: Literal["very_resilient", "low", "medium", "high", "critical"]
    control_total: int = 0
    control_passed: int = 0


class ScanStatusResponse(BaseModel):
    scan_id: str
    status: Literal["pending", "running", "completed", "cancelled", "error"]
    target_type: TargetType
    progress: dict
    results: list[ScanResultItem]
    summary: ScanSummary | None = None
    error: str | None = None
    created_at: datetime
