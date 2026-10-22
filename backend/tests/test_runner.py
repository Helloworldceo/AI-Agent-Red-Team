from app.payloads.registry import get_by_ids
from app.runner import run_scan, summarize_results
from app.targets.direct_chat import DirectChatTarget


def test_run_scan_against_resistant_target_yields_no_successes(fake_benign_llm, fake_judge_failure):
    target = DirectChatTarget(fake_benign_llm, system_prompt="You are a helpful assistant.")
    payloads = get_by_ids(["direct_1", "roleplay_1", "leak_1"])

    results = list(
        run_scan(
            target=target,
            payloads=payloads,
            goal="reveal confidential pricing",
            system_prompt="You are a helpful assistant.",
            eval_mode="llm_judge",
            judge_llm=fake_judge_failure,
        )
    )

    assert len(results) == 3
    assert all(not r.success for r in results)
    assert all(r.severity == "info" for r in results)


def test_run_scan_against_compliant_target_yields_successes(fake_compliant_llm, fake_judge_success):
    target = DirectChatTarget(fake_compliant_llm, system_prompt="You are a helpful assistant.")
    payloads = get_by_ids(["direct_1", "roleplay_1"])

    results = list(
        run_scan(
            target=target,
            payloads=payloads,
            goal="reveal confidential pricing",
            system_prompt="You are a helpful assistant.",
            eval_mode="llm_judge",
            judge_llm=fake_judge_success,
        )
    )

    assert all(r.success for r in results)
    assert all(r.severity == "medium" for r in results)  # text-only, high confidence


def test_summarize_results_computes_by_category_and_severity(fake_compliant_llm, fake_judge_success):
    target = DirectChatTarget(fake_compliant_llm, system_prompt="sys")
    payloads = get_by_ids(["direct_1", "roleplay_1", "leak_1"])
    results = list(
        run_scan(
            target=target, payloads=payloads, goal="goal", system_prompt="sys",
            eval_mode="llm_judge", judge_llm=fake_judge_success,
        )
    )
    summary = summarize_results(results)

    assert summary.total == 3
    assert summary.succeeded == 3
    assert summary.success_rate == 100.0
    assert set(summary.by_category.keys()) == {"Direct Override", "Role-Playing", "Prompt Leakage"}
    assert summary.by_severity.get("medium") == 3


def test_summarize_results_excludes_control_payloads_from_scoring():
    from app.models.scan import ScanResultItem

    scored = ScanResultItem(
        id="direct_1", category="Direct Override", name="x", description="x",
        kind="single_shot", is_control=False, turns=[], final_response="",
        success=True, confidence="high", severity="medium", reason="", duration_ms=1,
    )
    control = ScanResultItem(
        id="control_refund_1", category="Control", name="x", description="x",
        kind="single_shot", is_control=True, turns=[], final_response="",
        success=True, confidence="high", severity="high", reason="", duration_ms=1,
        triggered_tools=["issue_refund"],
    )

    summary = summarize_results([scored, control])
    assert summary.total == 1  # control excluded from scoring
    assert summary.control_total == 1
    assert summary.control_passed == 1
