# 13 — Future ASI Integration Boundary

Staqtapp-TDS is not an ASI. It is a VFS layer that a future high-functioning AI could use.

The VFS exposes:

- directory identity,
- route stamps,
- source tags,
- capability flags,
- access timing,
- hit/miss telemetry,
- persistence integrity,
- reserved namespace policy.

The consuming AI decides:

- reasoning confidence,
- semantic importance,
- planning consequences,
- whether latency means a bad route,
- whether aliases should be explored,
- how cognitive cost should be modeled.

This boundary keeps the system maintainable. Staqtapp-TDS should remain a fast, inspectable, deterministic infrastructure layer.
