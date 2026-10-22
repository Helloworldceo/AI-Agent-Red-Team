"""
In-memory scan-state store: a module-level dict guarded by a lock, swept for
stale entries. Sufficient for a single-user local tool. Phase-2: swap for a
SQLite-backed repository behind the same interface to persist history across
restarts.
"""

import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Literal

from app.models.payload import TargetType
from app.models.scan import ScanResultItem, ScanSummary

_TTL = timedelta(hours=1)


class ScanState:
    def __init__(self, scan_id: str, target_type: TargetType, total_payloads: int):
        self.id = scan_id
        self.target_type = target_type
        self.status: Literal["pending", "running", "completed", "cancelled", "error"] = "pending"
        self.results: list[ScanResultItem] = []
        self.summary: ScanSummary | None = None
        self.error: str | None = None
        self.created_at = datetime.now()
        self.total_payloads = total_payloads
        self.current_payload_name: str | None = None
        self.cancel_event = threading.Event()
        self._lock = threading.Lock()

    def append_result(self, item: ScanResultItem) -> None:
        with self._lock:
            self.results.append(item)
            self.current_payload_name = item.name

    def snapshot_results(self) -> list[ScanResultItem]:
        with self._lock:
            return list(self.results)


_SCANS: dict[str, ScanState] = {}
_STORE_LOCK = threading.Lock()


def _sweep_stale() -> None:
    cutoff = datetime.now() - _TTL
    stale = [sid for sid, s in _SCANS.items() if s.created_at < cutoff]
    for sid in stale:
        del _SCANS[sid]


def create_scan(target_type: TargetType, total_payloads: int) -> ScanState:
    with _STORE_LOCK:
        _sweep_stale()
        scan_id = uuid.uuid4().hex
        state = ScanState(scan_id, target_type, total_payloads)
        _SCANS[scan_id] = state
        return state


def get_scan(scan_id: str) -> ScanState | None:
    with _STORE_LOCK:
        return _SCANS.get(scan_id)
