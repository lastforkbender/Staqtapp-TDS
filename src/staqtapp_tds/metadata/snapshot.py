from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time

@dataclass(slots=True, frozen=True)
class RuntimeSnapshot:
    schema_version: int
    created_at: float = field(default_factory=time.time)
    uptime_seconds: float = 0.0
    performance: dict[str, Any] = field(default_factory=dict)
    storage: dict[str, Any] = field(default_factory=dict)
    indexes: dict[str, Any] = field(default_factory=dict)
    behavior: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version, "created_at": self.created_at,
            "uptime_seconds": self.uptime_seconds,
            "performance": dict(self.performance), "storage": dict(self.storage),
            "indexes": dict(self.indexes), "behavior": dict(self.behavior),
        }
