"""
Optional native EntryIndex boundary for v1.6.0.

No compiled extension is required for this release. This module documents the
import seam and lets the package select a future native backend without changing
TDSDirectory or the public API.
"""
from __future__ import annotations

from typing import Any


def load_native_backend(*, shards: int = 64) -> Any | None:
    """
    Try to load an optional compiled backend.

    Future target module name: staqtapp_tds_native.EntryIndexBackend
    Expected methods: put/get/get_handle/get_by_handle/pop/keys/values/items/contains/stats.
    Read methods should release the GIL internally when implemented in C/C++.
    """
    try:
        from staqtapp_tds_native import EntryIndexBackend  # type: ignore
    except Exception:
        return None
    return EntryIndexBackend(shards=shards)
