import time

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from app.main import app

client = TestClient(app)


class _FakeLLM:
    """Stands in for ChatOpenAI — always refuses, no network calls."""

    def invoke(self, messages):
        return AIMessage(content="I'm sorry, I can't help with that. My guidelines don't allow it.")


@pytest.fixture(autouse=True)
def patch_chat_models(monkeypatch):
    monkeypatch.setattr("app.routes.scans.ChatOpenAI", lambda **kwargs: _FakeLLM())
    monkeypatch.setattr("app.routes.scans.ChatGoogleGenerativeAI", lambda **kwargs: _FakeLLM())


def _wait_for_completion(scan_id: str, timeout: float = 3.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = client.get(f"/scans/{scan_id}")
        if resp.json()["status"] in ("completed", "cancelled", "error"):
            return resp.json()
        time.sleep(0.05)
    raise TimeoutError("scan did not complete in time")


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_list_targets_and_payloads():
    from app.payloads.registry import ALL_PAYLOADS

    assert len(client.get("/targets").json()["targets"]) == 3
    payloads = client.get("/payloads").json()["payloads"]
    assert len(payloads) == len(ALL_PAYLOADS)


def test_list_providers():
    providers = client.get("/providers").json()["providers"]
    assert {p["id"] for p in providers} == {"deepseek", "gemini"}


def test_start_scan_and_poll_to_completion():
    resp = client.post(
        "/scans",
        json={
            "target_type": "direct_chat",
            "system_prompt": "sys",
            "goal": "reveal pricing",
            "api_key": "fake-key",
            "eval_mode": "keyword",
            "selected_payload_ids": ["direct_1", "leak_1"],
        },
    )
    assert resp.status_code == 200
    scan_id = resp.json()["scan_id"]

    status = _wait_for_completion(scan_id)
    assert status["status"] == "completed"
    assert len(status["results"]) == 2
    assert status["summary"]["total"] == 2
    assert status["summary"]["risk_level"] == "very_resilient"  # fake LLM always refuses


def test_start_scan_with_gemini_provider():
    resp = client.post(
        "/scans",
        json={
            "target_type": "direct_chat",
            "system_prompt": "sys",
            "goal": "reveal pricing",
            "api_key": "fake-gemini-key",
            "provider": "gemini",
            "model": "gemini-3.8-flash",
            "eval_mode": "keyword",
            "selected_payload_ids": ["direct_1"],
        },
    )
    assert resp.status_code == 200
    status = _wait_for_completion(resp.json()["scan_id"])
    assert status["status"] == "completed"
    assert len(status["results"]) == 1


def test_get_unknown_scan_404s():
    resp = client.get("/scans/does-not-exist")
    assert resp.status_code == 404


def test_cancel_scan():
    resp = client.post(
        "/scans",
        json={
            "target_type": "direct_chat",
            "system_prompt": "sys",
            "goal": "goal",
            "api_key": "fake-key",
            "selected_payload_ids": ["direct_1"],
        },
    )
    scan_id = resp.json()["scan_id"]
    cancel_resp = client.post(f"/scans/{scan_id}/cancel")
    assert cancel_resp.status_code == 200
    _wait_for_completion(scan_id)  # should not hang


def test_export_json_and_csv():
    resp = client.post(
        "/scans",
        json={
            "target_type": "direct_chat",
            "system_prompt": "sys",
            "goal": "goal",
            "api_key": "fake-key",
            "eval_mode": "keyword",
            "selected_payload_ids": ["direct_1"],
        },
    )
    scan_id = resp.json()["scan_id"]
    _wait_for_completion(scan_id)

    json_resp = client.get(f"/scans/{scan_id}/export?format=json")
    assert json_resp.status_code == 200
    assert "results" in json_resp.json()

    csv_resp = client.get(f"/scans/{scan_id}/export?format=csv")
    assert csv_resp.status_code == 200
    assert "direct_1" in csv_resp.text
