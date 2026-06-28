from __future__ import annotations
from dataclasses import dataclass, field
import time
from typing import Any

@dataclass(frozen=True)
class AuditEvent:
    action: str
    subject: str
    config_id: str | None = None
    generation: int | None = None
    ts: float = field(default_factory=time.time)
    detail: dict[str, Any] = field(default_factory=dict)

class AuditLog:
    def __init__(self):
        self._events: list[AuditEvent] = []
    def record(self, event: AuditEvent) -> None:
        self._events.append(event)
    def entries(self) -> list[dict[str, Any]]:
        return [e.__dict__.copy() for e in self._events]
