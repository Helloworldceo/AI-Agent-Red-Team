from abc import ABC, abstractmethod

from app.models.trace import InjectionSpec, TargetInvocationResult


class BaseTarget(ABC):
    """
    Something a scan attacks. A single-shot payload is just a conversation
    of length 1 — single-shot and multi-turn payloads use the same method.
    """

    @abstractmethod
    def run_conversation(
        self,
        turns: list[str],
        injection: InjectionSpec | None = None,
    ) -> TargetInvocationResult: ...
