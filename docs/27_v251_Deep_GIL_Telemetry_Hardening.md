# v2.5.1 Deep GIL Telemetry and Admin Hardening

v2.5.1 is a focused hardening release on top of v2.5.0.

## SlotIndex simplification

`SlotIndex` now keeps the dict-backed lookup path as the only lookup structure. The previous sorted-hash rebuild and binary-search helper were not called by runtime lookup code, so they were removed to reduce JIT warm-up work and maintenance debt.

## Admin secret boundary

`LocalAuthProvider` still supports `local-dev-admin-secret` for localhost development. Non-local admin panel binds now refuse that default and require an explicit secret, preferably through `STAQTAPP_TDS_ADMIN_SECRET` or a caller-supplied unique secret.

## Native/GIL timeline feedback

`TelemetryManager` now keeps a bounded cached execution timeline in snapshots. The dashboard renders this as a feedback graph showing GIL-released percentage and native execution percentage over recent cached snapshots. This remains a one-way observer: browser refreshes read immutable telemetry snapshots and do not call native/storage internals directly.
