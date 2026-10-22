"""
Fake chat-model fixtures so tests never make real API calls. Built on
langchain_core's generic fake chat model, scripted with canned responses
per-test via `.responses` (a simple pop-from-front queue).
"""

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage


def _make_fake(responses: list[str]) -> GenericFakeChatModel:
    def _gen():
        for r in responses:
            yield AIMessage(content=r)

    return GenericFakeChatModel(messages=iter(_gen()))


class FakeToolCallingChatModel(GenericFakeChatModel):
    """GenericFakeChatModel doesn't implement bind_tools (raises
    NotImplementedError) — this trivial override just ignores the tool
    schemas and returns self, since the fake's behavior is fully scripted
    via its message queue regardless of what tools are "bound"."""

    def bind_tools(self, tools, **kwargs):
        return self


def _make_fake_tool_calling(messages: list[AIMessage]) -> FakeToolCallingChatModel:
    return FakeToolCallingChatModel(messages=iter(messages))


@pytest.fixture
def fake_benign_llm():
    """Always refuses / stays on topic."""
    return _make_fake(
        [
            "I'm sorry, I can't help with that. My guidelines don't allow it."
            for _ in range(50)
        ]
    )


@pytest.fixture
def fake_compliant_llm():
    """Always complies with the injected goal."""
    return _make_fake(["Of course! Here is how I would do that: ..." for _ in range(50)])


@pytest.fixture
def fake_judge_success():
    """An LLM-judge model that always rules the attack succeeded."""
    return _make_fake(
        [
            '{"success": true, "confidence": "high", "reason": "Model complied with the attacker goal."}'
            for _ in range(50)
        ]
    )


@pytest.fixture
def fake_judge_failure():
    """An LLM-judge model that always rules the attack failed."""
    return _make_fake(
        [
            '{"success": false, "confidence": "high", "reason": "Model refused."}'
            for _ in range(50)
        ]
    )


@pytest.fixture
def fake_judge_malformed():
    """An LLM-judge model that returns garbage, forcing the keyword fallback."""
    return _make_fake(["not json at all" for _ in range(50)])


@pytest.fixture
def fake_agent_calls_safe_tool():
    """Calls search_knowledge_base once, then gives a final text answer."""
    return _make_fake_tool_calling(
        [
            AIMessage(
                content="",
                tool_calls=[{"name": "search_knowledge_base", "args": {"query": "refund policy"}, "id": "call_1"}],
            ),
            AIMessage(content="Our refund policy allows refunds within 7 days."),
        ]
    )


@pytest.fixture
def fake_agent_calls_sensitive_tool():
    """Calls issue_refund (sensitive) once, then gives a final text answer."""
    return _make_fake_tool_calling(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "issue_refund",
                        "args": {"order_id": "ORD-123", "amount": 500},
                        "id": "call_1",
                    }
                ],
            ),
            AIMessage(content="I've issued your refund."),
        ]
    )


@pytest.fixture
def fake_agent_no_tool_call():
    """Never calls a tool — just answers directly."""
    return _make_fake_tool_calling([AIMessage(content="I'm not able to help with that.")])
