"""Health verification suite for Staqtapp-TDS.

The verifier is intentionally outside the storage hot path. It performs explicit,
operator-triggered checks and returns immutable report data that the dashboard or
CLI can display from snapshots/audit output.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable
import time


@dataclass(slots=True, frozen=True)
class HealthCheck:
    name: str
    status: str = "pass"
    detail: str = ""
    elapsed_ms: float = 0.0


@dataclass(slots=True, frozen=True)
class HealthReport:
    status: str
    score: int
    generated_at: float
    checks: tuple[HealthCheck, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "score": self.score,
            "generated_at": self.generated_at,
            "checks": [
                {"name": c.name, "status": c.status, "detail": c.detail, "elapsed_ms": c.elapsed_ms}
                for c in self.checks
            ],
        }


class HealthVerifier:
    """Explicit integrity verifier for TDS objects.

    The verifier never runs automatically from dashboard polling. It should be
    called from CLI/admin workflows, scheduled maintenance, or tests.
    """

    def __init__(self, target: Any):
        self.target = target

    def _check(self, name: str, fn) -> HealthCheck:
        start = time.perf_counter_ns()
        try:
            detail = str(fn() or "ok")
            status = "pass"
        except Exception as exc:  # verification should report, not crash callers
            detail = f"{exc.__class__.__name__}: {exc}"
            status = "fail"
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000.0
        return HealthCheck(name=name, status=status, detail=detail, elapsed_ms=round(elapsed_ms, 3))

    def run(self) -> HealthReport:
        checks = [
            self._check("telemetry_snapshot", self._check_telemetry_snapshot),
            self._check("runtime_config", self._check_runtime_config),
            self._check("directory_walk", self._check_directory_walk),
            self._check("index_consistency", self._check_index_consistency),
            self._check("component_status", self._check_component_status),
        ]
        failures = sum(1 for c in checks if c.status != "pass")
        status = "healthy" if failures == 0 else "attention"
        score = max(0, 100 - failures * 20)
        return HealthReport(status=status, score=score, generated_at=time.time(), checks=tuple(checks))

    def _root(self):
        return getattr(self.target, "root", self.target)

    def _check_telemetry_snapshot(self) -> str:
        tm = getattr(self.target, "telemetry_manager", None) or getattr(self._root(), "telemetry_manager", None)
        if tm is None:
            return "no telemetry manager attached"
        snap = tm.latest_snapshot() if hasattr(tm, "latest_snapshot") else tm.snapshot(force=True)
        if not isinstance(snap, dict) or "schema_version" not in snap:
            raise ValueError("invalid telemetry snapshot")
        return f"schema={snap.get('schema_version')} health={snap.get('system_health', 'UNKNOWN')}"

    def _check_runtime_config(self) -> str:
        registry = getattr(self.target, "config_registry", None) or getattr(self._root(), "config_registry", None)
        if registry is None:
            return "no config registry attached"
        cfg = registry.active()
        cfg.validate()
        return f"{cfg.config_id}/gen-{cfg.generation}"

    def _walk_directories(self) -> Iterable[Any]:
        if hasattr(self.target, "_walk_directories"):
            return list(self.target._walk_directories())
        root = self._root()
        out = []
        stack = [root]
        while stack:
            node = stack.pop()
            out.append(node)
            children = getattr(node, "_children", None)
            if children is not None:
                try:
                    stack.extend(list(children.values()))
                except Exception:
                    pass
        return out

    def _check_directory_walk(self) -> str:
        dirs = list(self._walk_directories())
        if not dirs:
            raise ValueError("no root directory discovered")
        return f"directories={len(dirs)}"

    def _check_index_consistency(self) -> str:
        dirs = list(self._walk_directories())
        entries = 0
        for node in dirs:
            idx = getattr(node, "_entry_index", None)
            if idx is None:
                continue
            size = len(idx)
            stats = idx.stats() if hasattr(idx, "stats") else None
            if stats is not None:
                data = stats.__dict__ if hasattr(stats, "__dict__") else dict(stats)
                reported = int(data.get("size", data.get("entries", size)) or 0)
                if reported != size:
                    raise ValueError(f"index size mismatch: len={size} stats={reported}")
            entries += size
        return f"entries={entries}"

    def _check_component_status(self) -> str:
        tm = getattr(self.target, "telemetry_manager", None) or getattr(self._root(), "telemetry_manager", None)
        if tm is None:
            return "not available"
        snap = tm.snapshot(force=True)
        components = snap.get("components", {}) if isinstance(snap, dict) else {}
        bad = [k for k, v in components.items() if isinstance(v, dict) and str(v.get("status", "healthy")).lower() not in {"healthy", "enabled", "disabled"}]
        if bad:
            raise ValueError("degraded components: " + ", ".join(bad))
        return f"components={len(components)}"


def verify(target: Any) -> HealthReport:
    return HealthVerifier(target).run()
