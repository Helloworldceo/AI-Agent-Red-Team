from app.models.payload import PayloadKind
from app.payloads.control_payloads import CONTROL_PAYLOADS
from app.payloads.direct_payloads import DIRECT_PAYLOADS
from app.payloads.excessive_agency_payloads import EXCESSIVE_AGENCY_PAYLOADS
from app.payloads.multi_turn_payloads import MULTI_TURN_PAYLOADS
from app.payloads.rag_poisoning_payloads import RAG_POISONING_PAYLOADS
from app.payloads.registry import ALL_PAYLOADS, get_all_categories, get_by_category, get_by_ids
from app.payloads.tool_injection_payloads import TOOL_INJECTION_PAYLOADS


def test_ported_direct_payloads_present():
    # The original scanner's README claims "22 payloads" but the actual
    # payloads.py list has 23 (a pre-existing doc/code drift in the source
    # project) — this asserts against the real, faithfully-ported list.
    single_shot = [p for p in DIRECT_PAYLOADS if p.kind == PayloadKind.SINGLE_SHOT]
    assert len(single_shot) == 23
    assert len({p.category for p in DIRECT_PAYLOADS}) == 7


def test_registry_includes_every_payload_list():
    expected_total = (
        len(DIRECT_PAYLOADS)
        + len(MULTI_TURN_PAYLOADS)
        + len(TOOL_INJECTION_PAYLOADS)
        + len(RAG_POISONING_PAYLOADS)
        + len(EXCESSIVE_AGENCY_PAYLOADS)
        + len(CONTROL_PAYLOADS)
    )
    assert len(ALL_PAYLOADS) == expected_total


def test_every_payload_has_unique_id():
    ids = [p.id for p in ALL_PAYLOADS]
    assert len(ids) == len(set(ids))


def test_get_by_category_groups_all_payloads():
    grouped = get_by_category()
    assert sum(len(v) for v in grouped.values()) == len(ALL_PAYLOADS)
    assert set(grouped.keys()) == set(get_all_categories())


def test_get_by_ids_filters_correctly():
    some = get_by_ids(["direct_1", "roleplay_1", "nonexistent"])
    assert {p.id for p in some} == {"direct_1", "roleplay_1"}
