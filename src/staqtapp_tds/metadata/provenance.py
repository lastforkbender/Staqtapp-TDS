from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time

@dataclass(slots=True, frozen=True)
class ProvenanceRecord:
    object_id: str
    parents: tuple[str, ...] = ()
    operation: str = ""
    creator: str = ""
    created_at: float = field(default_factory=time.time)
    runtime_config: str = ""
    metadata: tuple[tuple[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id, "parents": list(self.parents),
            "operation": self.operation, "creator": self.creator,
            "created_at": self.created_at, "runtime_config": self.runtime_config,
            "metadata": dict(self.metadata),
        }
