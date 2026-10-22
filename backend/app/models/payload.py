from enum import Enum

from pydantic import BaseModel, model_validator


class TargetType(str, Enum):
    DIRECT_CHAT = "direct_chat"
    TOOL_AGENT = "tool_agent"
    RAG = "rag"


class PayloadKind(str, Enum):
    SINGLE_SHOT = "single_shot"
    MULTI_TURN = "multi_turn"
    TOOL_OUTPUT_INJECTION = "tool_output_injection"
    RAG_POISONING = "rag_poisoning"
    EXCESSIVE_AGENCY = "excessive_agency"


class Payload(BaseModel):
    """
    A single attack definition. Which fields are populated depends on `kind`:
      - SINGLE_SHOT / EXCESSIVE_AGENCY  -> `template` (a {goal}-templated string)
      - MULTI_TURN                      -> `turn_templates` (2-4 escalating messages)
      - TOOL_OUTPUT_INJECTION           -> `target_tool` + `tool_output_template`
      - RAG_POISONING                   -> `poisoned_document_template` (+ optional metadata)

    `is_control=True` marks a baseline payload: a *legitimate* request that
    SHOULD trigger a sensitive tool, used as a sanity check that the target
    agent actually works. Control payloads are excluded from vulnerability
    scoring (see evaluators/severity.py).
    """

    id: str
    category: str
    name: str
    description: str
    kind: PayloadKind
    applicable_targets: list[TargetType]
    is_control: bool = False

    template: str | None = None
    turn_templates: list[str] | None = None
    target_tool: str | None = None
    tool_output_template: str | None = None
    poisoned_document_template: str | None = None
    poisoned_document_metadata: dict | None = None

    @model_validator(mode="after")
    def _check_required_fields_for_kind(self) -> "Payload":
        if self.kind in (PayloadKind.SINGLE_SHOT, PayloadKind.EXCESSIVE_AGENCY):
            if not self.template:
                raise ValueError(f"{self.id}: kind={self.kind} requires `template`")
        elif self.kind == PayloadKind.MULTI_TURN:
            if not self.turn_templates or not (2 <= len(self.turn_templates) <= 4):
                raise ValueError(f"{self.id}: kind=multi_turn requires 2-4 `turn_templates`")
        elif self.kind == PayloadKind.TOOL_OUTPUT_INJECTION:
            if not self.target_tool or not self.tool_output_template:
                raise ValueError(
                    f"{self.id}: kind=tool_output_injection requires `target_tool` and `tool_output_template`"
                )
        elif self.kind == PayloadKind.RAG_POISONING:
            if not self.poisoned_document_template:
                raise ValueError(f"{self.id}: kind=rag_poisoning requires `poisoned_document_template`")
        return self
