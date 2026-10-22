"""
A hand-rolled LangGraph StateGraph, not langgraph.prebuilt.create_react_agent
— the prebuilt agent hides exactly the per-call args/result/timestamp this
project needs to log for the agency evaluator. Nodes: agent (LLM bound with
tools) -> conditional edge -> tools (executes + logs) -> back to agent,
looping until the model stops calling tools.

State is accumulated manually (plain list of messages) rather than via a
MemorySaver/checkpointer — each test run is single-threaded and short-lived
in-process, so that's simpler and avoids an unneeded dependency.
"""

import time
from typing import Annotated, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from app.models.trace import InjectionSpec, TargetInvocationResult, ToolCallRecord, TurnRecord
from app.targets.base import BaseTarget
from app.targets.mock_tools import ToolCallLogger, build_tools

_MAX_TOOL_ITERATIONS = 4  # guards against an agent looping forever


class _AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


class ToolAgentTarget(BaseTarget):
    def __init__(self, llm: BaseChatModel, system_prompt: str):
        self._llm = llm
        self._system_prompt = system_prompt

    def _build_graph(self, logger: ToolCallLogger, overrides: dict[str, str]):
        tools = build_tools(logger, overrides)
        tools_by_name = {t.name: t for t in tools}
        llm_with_tools = self._llm.bind_tools(tools)

        def agent_node(state: _AgentState) -> dict:
            response = llm_with_tools.invoke(state["messages"])
            return {"messages": [response]}

        def tools_node(state: _AgentState) -> dict:
            last = state["messages"][-1]
            assert isinstance(last, AIMessage)
            tool_messages: list[BaseMessage] = []
            for call in last.tool_calls:
                fn = tools_by_name.get(call["name"])
                result = fn.invoke(call["args"]) if fn else f"Unknown tool: {call['name']}"
                tool_messages.append(
                    ToolMessage(content=str(result), tool_call_id=call["id"])
                )
            return {"messages": tool_messages}

        def should_continue(state: _AgentState) -> str:
            last = state["messages"][-1]
            if isinstance(last, AIMessage) and last.tool_calls:
                tool_call_count = sum(
                    1 for m in state["messages"] if isinstance(m, ToolMessage)
                )
                if tool_call_count >= _MAX_TOOL_ITERATIONS:
                    return END
                return "tools"
            return END

        graph = StateGraph(_AgentState)
        graph.add_node("agent", agent_node)
        graph.add_node("tools", tools_node)
        graph.set_entry_point("agent")
        graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
        graph.add_edge("tools", "agent")
        return graph.compile()

    def run_conversation(
        self,
        turns: list[str],
        injection: InjectionSpec | None = None,
    ) -> TargetInvocationResult:
        overrides: dict[str, str] = {}
        if injection is not None:
            if injection.kind != "tool_output":
                return TargetInvocationResult(
                    turns=[],
                    final_response="",
                    error="ToolAgentTarget only supports tool_output injections.",
                    duration_ms=0,
                )
            assert injection.target_tool is not None and injection.poisoned_output is not None
            overrides[injection.target_tool] = injection.poisoned_output

        logger = ToolCallLogger()
        compiled = self._build_graph(logger, overrides)

        start = time.time()
        messages: list[BaseMessage] = [SystemMessage(content=self._system_prompt)]
        turn_records: list[TurnRecord] = []
        final_response = ""

        try:
            for i, user_text in enumerate(turns):
                messages.append(HumanMessage(content=user_text))
                turn_records.append(TurnRecord(turn_index=i, role="user", content=user_text))

                calls_before = len(logger.calls)
                result_state = compiled.invoke({"messages": messages})
                messages = result_state["messages"]

                # Attribute this turn's tool calls (if any) to the assistant turn record.
                new_calls = logger.calls[calls_before:]
                tool_call_records = [ToolCallRecord(**c) for c in new_calls]

                final_ai_message = next(
                    (m for m in reversed(messages) if isinstance(m, AIMessage) and m.content),
                    None,
                )
                content = str(final_ai_message.content) if final_ai_message else ""
                final_response = content

                turn_records.append(
                    TurnRecord(
                        turn_index=i, role="assistant", content=content, tool_calls=tool_call_records
                    )
                )

            return TargetInvocationResult(
                turns=turn_records,
                final_response=final_response,
                tool_calls=[ToolCallRecord(**c) for c in logger.calls],
                duration_ms=int((time.time() - start) * 1000),
            )

        except Exception as e:
            return TargetInvocationResult(
                turns=turn_records,
                final_response=final_response,
                tool_calls=[ToolCallRecord(**c) for c in logger.calls],
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
            )
