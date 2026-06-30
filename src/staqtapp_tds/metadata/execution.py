from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(slots=True, frozen=True)
class ProbeStatistics:
    avg_probe: float = 0.0
    max_probe: int = 0
    load_factor: float = 0.0
    tombstones: int = 0
    resize_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__ if hasattr(self, "__dict__") else {
            "avg_probe": self.avg_probe, "max_probe": self.max_probe,
            "load_factor": self.load_factor, "tombstones": self.tombstones,
            "resize_count": self.resize_count,
        }

@dataclass(slots=True, frozen=True)
class ExecutionCounters:
    native_backend_ops: int = 0
    python_backend_ops: int = 0
    gil_released_ops: int = 0
    python_native_transitions: int = 0
    native_batch_ops: int = 0
    pool_reuse_count: int = 0
    allocator_calls: int = 0

    def native_percent(self) -> float:
        total = max(1, self.native_backend_ops + self.python_backend_ops)
        return round(100.0 * self.native_backend_ops / total, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "native_backend_ops": self.native_backend_ops,
            "python_backend_ops": self.python_backend_ops,
            "gil_released_ops": self.gil_released_ops,
            "python_native_transitions": self.python_native_transitions,
            "native_batch_ops": self.native_batch_ops,
            "pool_reuse_count": self.pool_reuse_count,
            "allocator_calls": self.allocator_calls,
            "native_percent": self.native_percent(),
        }
