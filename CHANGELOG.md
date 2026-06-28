# Changelog

## v1.7.3 — Storage Refinement & Invariant Feedback

- Added `serializers.py` with payload-kind policy and content hashing.
- Added optional `orjson`/`simdjson` acceleration where available.
- Added automatic variable serializer selection for JSON-safe values, NumPy arrays, and pickle-only Python objects.
- Added per-entry metadata: payload kind, content hash, raw size, stored size, and compression status.
- Added compression threshold policy.
- Added `write_json()`.
- Added `write_text_chunked()` and transparent `read_text()` reconstruction for chunked text entries.
- Added `invariants.py` with Numba/NumPy-friendly invariant records.
- Added invariant checks for lock/stalk consistency, entry-count limits, and latency hard-limit violations.
- Preserved the clean `EntryIndex` seam; serialization and variable logic remain above the index.
- Expanded tests to 25 passing tests.

## v1.7.2

Documentation and stabilization release.

### Added

- Full engineering documentation under `docs/`.
- Rewritten root `README.md`.
- Reserved namespace support via `ReservedNamespaces`.
- Manifest `reserved_namespaces` block.
- `TDSDirectory.is_reserved_namespace()`.
- `TDSDirectory.reserved_namespace_names()`.
- `mkdir(..., allow_reserved=True)` escape hatch for explicit creation.
- Reserved namespace unit test.

### Changed

- Version bumped to `1.7.2`.
- Metadata sidecar now includes reserved namespace policy snapshot.

### Not changed

- No C/C++ backend yet.
- No new telemetry algorithm.
- No expanded manifest hot-path work.
- No change to SRZ cognitive boundary.

## v1.7.0

Semantic infrastructure release.

- Inherited read-once manifest policy.
- Optional Semantic Routing Zones.
- Directory telemetry modes.
- Latency buckets.
- Capability registry.
- Persistence of SRZ and telemetry snapshots.

## v1.7.2 — Variable Control & Text Payload Release

### Added
- `result.py` with non-halting `TDSResult` statuses for AI/agent-safe writes.
- `errors.py` with lightweight OFF/LIGHT/TRACE error telemetry.
- `variables.py` implementing the original Staqtapp variable-control identity layer:
  - `addvar()`
  - `editvar()`
  - `lockvar()` / `unlockvar()`
  - `stalkvar()`
  - `findvar()` / `loadvar()`
- First-class UTF-8 text storage through `write_text()` / `read_text()`.
- `FmtID.TEXT_UTF8` and `FmtID.JSON_UTF8` payload lanes.
- Persistence of variable lock/stalk control tables in `.tds.meta`.
- Tests for duplicate variables, locked writes, stalk-chain exactness, text overwrite behavior, and persistence roundtrips.

### Design
- Duplicate names now return structured conflict feedback instead of throwing normal operational exceptions.
- `stalkvar("~name", data)` creates materialized residual increments from the latest tracked value.
- `stalkvar("name", None)` clears tracked increments while preserving the base value.
- `stalkvar("name", data)` clears tracked increments and replaces the base value.
- Text files and Python variables share directory namespace identity but use separate APIs.

### Validation
- Test suite: 19 passed.
