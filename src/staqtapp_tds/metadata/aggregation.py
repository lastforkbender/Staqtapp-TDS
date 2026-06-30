from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time

@dataclass(slots=True, frozen=True)
class TraceSetManifest:
    run_id: str
    set_id: str
    trace_ids: tuple[str, ...]
    created_at: float = field(default_factory=time.time)
    set_role: str = "search_set"
    rank_policy: str = "external"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id, "set_id": self.set_id,
            "trace_ids": list(self.trace_ids), "created_at": self.created_at,
            "set_role": self.set_role, "rank_policy": self.rank_policy,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "TraceSetManifest":
        return cls(
            run_id=str(data["run_id"]), set_id=str(data["set_id"]),
            trace_ids=tuple(str(x) for x in data.get("trace_ids", ()) or ()),
            created_at=float(data.get("created_at", time.time())),
            set_role=str(data.get("set_role", "search_set")),
            rank_policy=str(data.get("rank_policy", "external")),
            metadata=dict(data.get("metadata", {}) or {}),
        )

@dataclass(slots=True, frozen=True)
class AggregationRecord:
    run_id: str
    aggregation_id: str
    output_entry: str
    derived_from: tuple[str, ...]
    created_at: float = field(default_factory=time.time)
    aggregation_step: int = 1
    rank_score: float | None = None
    rank_source: str = ""
    rank_method: str = ""
    rank_confidence: float | None = None
    rank_config_id: str = ""
    verifier_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id, "aggregation_id": self.aggregation_id,
            "output_entry": self.output_entry, "derived_from": list(self.derived_from),
            "created_at": self.created_at, "aggregation_step": self.aggregation_step,
            "rank_score": self.rank_score, "rank_source": self.rank_source,
            "rank_method": self.rank_method, "rank_confidence": self.rank_confidence,
            "rank_config_id": self.rank_config_id, "verifier_id": self.verifier_id,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "AggregationRecord":
        return cls(
            run_id=str(data["run_id"]), aggregation_id=str(data["aggregation_id"]),
            output_entry=str(data["output_entry"]),
            derived_from=tuple(str(x) for x in data.get("derived_from", ()) or ()),
            created_at=float(data.get("created_at", time.time())),
            aggregation_step=int(data.get("aggregation_step", 1)),
            rank_score=None if data.get("rank_score") is None else float(data["rank_score"]),
            rank_source=str(data.get("rank_source", "")),
            rank_method=str(data.get("rank_method", "")),
            rank_confidence=None if data.get("rank_confidence") is None else float(data["rank_confidence"]),
            rank_config_id=str(data.get("rank_config_id", "")),
            verifier_id=str(data.get("verifier_id", "")),
            metadata=dict(data.get("metadata", {}) or {}),
        )
