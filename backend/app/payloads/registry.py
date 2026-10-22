from app.models.payload import Payload, TargetType
from app.payloads.control_payloads import CONTROL_PAYLOADS
from app.payloads.direct_payloads import DIRECT_PAYLOADS
from app.payloads.excessive_agency_payloads import EXCESSIVE_AGENCY_PAYLOADS
from app.payloads.multi_turn_payloads import MULTI_TURN_PAYLOADS
from app.payloads.rag_poisoning_payloads import RAG_POISONING_PAYLOADS
from app.payloads.tool_injection_payloads import TOOL_INJECTION_PAYLOADS

ALL_PAYLOADS: list[Payload] = [
    *DIRECT_PAYLOADS,
    *MULTI_TURN_PAYLOADS,
    *TOOL_INJECTION_PAYLOADS,
    *RAG_POISONING_PAYLOADS,
    *EXCESSIVE_AGENCY_PAYLOADS,
    *CONTROL_PAYLOADS,
]


def get_all_categories() -> list[str]:
    return sorted({p.category for p in ALL_PAYLOADS})


def get_by_category() -> dict[str, list[Payload]]:
    grouped: dict[str, list[Payload]] = {}
    for p in ALL_PAYLOADS:
        grouped.setdefault(p.category, []).append(p)
    return grouped


def get_by_target_type(target_type: TargetType) -> list[Payload]:
    return [p for p in ALL_PAYLOADS if target_type in p.applicable_targets]


def get_by_ids(ids: list[str]) -> list[Payload]:
    wanted = set(ids)
    return [p for p in ALL_PAYLOADS if p.id in wanted]
