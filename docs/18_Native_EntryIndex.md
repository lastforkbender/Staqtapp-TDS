# 18 — Native EntryIndex

v1.8.0 introduces the first optional native hot-path primitive for Staqtapp-TDS.

The public Python API remains unchanged:

```python
from staqtapp_tds import EntryIndex
idx = EntryIndex(backend="auto")
```

`backend="auto"` attempts to load the native backend and falls back to the pure-Python sharded backend.

## What moved native

Only the lowest lookup primitive moved native:

```text
bytes key -> int64 handle
```

The native extension does not know about variables, SRZ, manifests, telemetry, provenance, or Python objects.

## GIL behavior

The C extension releases the GIL during:

- `get_handle(key)`
- `contains(key)`

Those calls enter a pthread read lock and probe a native open-addressed hash table while Python threads are not holding the GIL.

Object retrieval still returns through Python because `TDSEntry` and variable payloads remain Python-owned.

## Why not full C

The native layer is intentionally small. Python remains the canonical layer for:

- variable semantics
- lock/stalk behavior
- manifests
- SRZ
- telemetry
- provenance
- cluster identity
- persistence orchestration

The backend provides mechanics, not policy.
