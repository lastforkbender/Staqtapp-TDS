# Staqtapp-TDS v2.3.5

Professional observability dashboard release. Adds the polished dark blue/purple/orange admin interface, expanded SVG icon set, Live Architecture panel, Timeline view, and snapshot-only JavaScript rendering while preserving the TDS hot-path boundary.

# Changelog

## 2.3.1

- Rebuilt the admin browser panel as a real packaged dashboard subsystem instead of a monolithic HTML string.
- Added dark Staqtapp-TDS telemetry theme matching the selected blue/purple/orange dashboard direction.
- Added packaged SVG icons, CSS, and JavaScript under `src/staqtapp_tds/admin/static/`.
- Added `templates/dashboard.html` for maintainable dashboard layout.
- Kept `/status.json` as the only auto-refresh data source so the browser remains a snapshot observer.
- Extended native Swiss-table stats scan to release the GIL during the probe-statistics scan.


## v2.3.0 — Observation Layer and Adaptive Dashboard

- Added `TelemetryManager`, a low-interference observation layer for dashboard-safe metrics.
- Added cached telemetry snapshots with schema versioning and a default 2-second refresh interval.
- Added performance metrics: reads/sec, writes/sec, lookup rate, average read/write/lookup latency, native/Python backend operation counts.
- Added storage metrics: raw/stored bytes, compression ratio, chunks created, deletes, errors, active config generation.
- Added index/routing metrics through throttled samplers: Swiss-entry totals, average/max probe, backend distribution, radix nodes/edges/depth/traversal averages.
- Added behavior classification: idle, read-heavy, write-heavy, balanced, plus basic storage-pressure status.
- Added conservative recommendation hooks for low compression gain, Swiss probe pressure, and miss-heavy lookups.
- Upgraded the local browser panel with performance, behavior, compression, index-pressure, and architecture feedback cards.
- Kept the dashboard observer-only: no repeated radix scans, deep diagnostics, benchmark runs, or repair actions are triggered by browser refresh.
- Added admin status support for an optional observation source.
- Added v2.3.0 tests for telemetry snapshots, threaded metric updates, dashboard HTML contract, panel status observation, and chunk metrics.

Validation:

- `pytest`: 47 passed, 2 skipped.
- Compile check: passed.

## v2.2.9 — Dark Theme Browser Panel Hardening

- Added dark blue/purple/orange browser panel theme.
- Added snapshot-driven Live Architecture dashboard.
- Added conservative 2s `/status.json` polling.
- Kept diagnostics/benchmarks out of automatic dashboard refresh.
- Added logo asset under docs.
- Added non-interference/theme tests.

## v2.2.0 — Admin Control Plane

- Added immutable `RuntimeConfig`, `AdminConfig`, and `ConfigRegistry`.
- Added optional local browser admin panel and CLI entrypoint.
- Added short-lived local config grants and append-only in-memory audit events.
- Added per-entry config provenance metadata (`config_id`, `config_generation`, `key_id`).
- Kept admin/security control-plane logic outside radix, native index, and read hot paths.

## v2.1.0 — Measured GIL, Chunking, and Table-Depth Seams

- Added EntryIndex.get_handles() for batch handle lookup; native backend releases the GIL across the batch lookup loop.
- Moved the native pop lookup/delete path under GIL-released native locking.
- Extended native Swiss-table stats with tombstones, load factor, max probe, and average probe length.
- Changed chunked text splitting to UTF-8 byte-budget chunks that never split a code point.
- Added radix router stats for max depth, average edge length, and average lookup steps.
- Added tests covering Unicode chunking, batch lookups, tombstone reuse, and radix observability.
