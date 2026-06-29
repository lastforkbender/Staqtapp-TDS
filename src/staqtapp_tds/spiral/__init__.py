"""Optional Spiral-compatible trace/provenance support.

This package does not implement Spiral reasoning. It provides neutral TDS storage
helpers for trace runs, trace-set manifests, aggregation records, ranking metadata,
and provenance links.
"""
from staqtapp_tds.spiral.trace import TraceRecord, TraceRole
from staqtapp_tds.spiral.manifest import TraceSetManifest
from staqtapp_tds.spiral.provenance import AggregationRecord
from staqtapp_tds.spiral.run import SpiralRun, SpiralRunMetadata, create_spiral_run, DEFAULT_SPIRAL_ROOT

__all__ = [
    "TraceRecord", "TraceRole", "TraceSetManifest", "AggregationRecord",
    "SpiralRun", "SpiralRunMetadata", "create_spiral_run", "DEFAULT_SPIRAL_ROOT",
]
