# Staqtapp-TDS v2.5.0

## v2.5.0 — Hardening and One-Way Telemetry

- Added `TelemetryLevel` with `OFF`, `MINIMAL`, `NORMAL`, `ENGINEERING`, and `DEVELOPER` snapshot detail modes.
- Added `TelemetryPublisherThread` so dashboards/exporters read the latest immutable snapshot instead of triggering storage-engine sampling directly.
- Added health state to observation snapshots: status, score, degraded components, snapshot age, telemetry level, and publisher timing.
- Added `staqtapp_tds.verify` with explicit health checks for telemetry snapshots, runtime config, directory traversal, index consistency, and component status.
- Added CLI health verification with `staqtapp-tds-admin verify`.
- Added `RuntimeConfig.telemetry_level` validation for deployment-specific observability levels.
- Added optional native sanitizer build hooks through `STAQTAPP_TDS_SANITIZE`.
- Preserved the dashboard as a separated snapshot-only subsystem; hardening checks are explicit and never run from normal dashboard polling.
- Kept v2.4.2 slotted metadata, native batch paths, checksum/chunk helpers, and memory-pool telemetry intact.

## v2.4.0 — Native Performance Expansion

- Added execution-mode telemetry for native %, Python %, GIL-released %, batch operations, and Python↔native transition rate.
- Added native Swiss-table counters for put, lookup, batch lookup, pop, stats, GIL-released calls, and transitions.
- Changed the native Swiss-table put path to release the GIL while performing native table insertion/update.
- Preserved the professional dashboard as a separated snapshot-only subsystem.
- Added dashboard fields for native execution and Python/native boundary activity.
- Added tests for execution telemetry, native execution counters, and dashboard fields.

## v2.3.7 — Optional Spiral-Compatible Trace Support

- Added `staqtapp_tds.spiral` optional workflow module.
- Added directory-first Spiral-style run helpers:
  - `create_spiral_run()`
  - `SpiralRun.store_search_trace()`
  - `SpiralRun.create_trace_set()`
  - `SpiralRun.store_aggregation()`
  - `SpiralRun.store_final()`
- Added neutral metadata records:
  - `TraceRecord`
  - `TraceSetManifest`
  - `AggregationRecord`
- Added external trace-rank metadata storage without making TDS perform ranking.
- Added Spiral/pipeline telemetry counters to `TelemetryManager` snapshots.
- Added `RuntimeConfig.spiral_support_enabled` policy flag.
- Updated README to reflect current telemetry, semantic storage, professional dashboard, and optional Spiral trace workflow support.
- Cleaned old runtime-source version banners so package versioning is centralized.

## v2.3.5 — Professional Dashboard

- Added professional dark blue/purple/orange admin dashboard structure.
- Added packaged HTML, CSS, JS, and SVG admin assets.
- Added live architecture, timeline, and recommendation-oriented dashboard sections.
- Preserved snapshot-only dashboard refresh behavior.

## v2.3.0 — Observation Layer

- Added `TelemetryManager` and cached dashboard-facing snapshots.
- Added low-interference performance, storage, behavior, index, and recommendation telemetry.

## v2.2.x — Admin Control Plane

- Added local admin panel, RuntimeConfig generation staging/promotion/rollback, local grants, and audit log.

## v2.1.x — Performance Seams

- Added UTF-8 byte-safe chunking, batch EntryIndex lookup, native backend seams, and stronger radix/Swiss-table measurements.
