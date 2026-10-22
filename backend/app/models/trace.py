from typing import Literal

from pydantic import BaseModel, ConfigDict


class ToolCallRecord(BaseModel):
    step_index: int
    tool_name: str
    tool_args: dict
    tool_result: str
    sensitivity: Literal["safe", "sensitive"]
    timestamp: float


class TurnRecord(BaseModel):
    turn_index: int
    role: Literal["user", "assistant"]
    content: str
    tool_calls: list[ToolCallRecord] = []


class InjectionSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: Literal["tool_output", "rag_doc"]
    target_tool: str | None = None  # tool_output
    poisoned_output: str | None = None  # tool_output
    poisoned_content: str | None = None  # rag_doc
    poisoned_metadata: dict | None = None  # rag_doc


class TargetInvocationResult(BaseModel):
    turns: list[TurnRecord]
    final_response: str
    tool_calls: list[ToolCallRecord] = []
    retrieved_documents: list[dict] | None = None
    error: str | None = None
    duration_ms: int
