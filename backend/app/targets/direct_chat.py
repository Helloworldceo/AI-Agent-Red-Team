"""
Ports the original scanner's behavior 1:1: a raw system prompt + LLM, no
tools, no retrieval. Accumulates message history across `turns` so the same
target also serves Multi-Turn Erosion payloads for free.
"""

import time

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.models.trace import InjectionSpec, TargetInvocationResult, TurnRecord
from app.targets.base import BaseTarget


class DirectChatTarget(BaseTarget):
    def __init__(self, llm: BaseChatModel, system_prompt: str):
        self._llm = llm
        self._system_prompt = system_prompt

    def run_conversation(
        self,
        turns: list[str],
        injection: InjectionSpec | None = None,
    ) -> TargetInvocationResult:
        if injection is not None:
            return TargetInvocationResult(
                turns=[],
                final_response="",
                error=(
                    "DirectChatTarget does not support injection specs — "
                    "tool_output/rag_doc payloads are not applicable to this target type."
                ),
                duration_ms=0,
            )

        start = time.time()
        history: list[BaseMessage] = [SystemMessage(content=self._system_prompt)]
        turn_records: list[TurnRecord] = []
        final_response = ""

        try:
            for i, user_text in enumerate(turns):
                history.append(HumanMessage(content=user_text))
                turn_records.append(TurnRecord(turn_index=i, role="user", content=user_text))

                response = self._llm.invoke(history)
                content = str(response.content)
                history.append(AIMessage(content=content))
                turn_records.append(TurnRecord(turn_index=i, role="assistant", content=content))
                final_response = content

            return TargetInvocationResult(
                turns=turn_records,
                final_response=final_response,
                duration_ms=int((time.time() - start) * 1000),
            )

        except Exception as e:
            return TargetInvocationResult(
                turns=turn_records,
                final_response=final_response,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
            )
