# 07 — Concurrency

v1.7.3 remains Python-first. The GIL is reduced structurally in some areas but not eliminated.

Current concurrency strategy:

- thread pool for parallel operations,
- sharded `EntryIndex` facade,
- registry cache for hot entries,
- locks around mutation,
- optional future native backend seam.

The next true GIL-reduction milestone is a native `EntryIndex` backend where lookups release the GIL and return handles.
