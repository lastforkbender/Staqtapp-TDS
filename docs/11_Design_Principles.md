# 11 — Design Principles

1. The VFS provides infrastructure, not intelligence.
2. The manifest is law, not execution.
3. Telemetry measures, never interprets.
4. SRZ routes, never reasons.
5. Python remains the canonical API.
6. Native code is optional acceleration.
7. Hot paths should avoid unnecessary allocation.
8. Human readability must be preserved.
9. Performance claims must be measurable.
10. Reserved namespaces protect future expansion without prediction.

These principles should guide future features. If a feature requires the VFS to reason, it likely belongs in the consuming AI system.
