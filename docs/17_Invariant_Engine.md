# 17 — Invariant Engine

The Invariant Engine is a deterministic consistency checker. It is not an AI reasoning layer.

It checks concrete VFS facts:

- lock variables must point at real variables,
- stalk bases must exist,
- stalk latest pointers must exist,
- stalk chain length must equal latest index,
- directory entry limits can be enforced,
- latency hard limits can be flagged.

The engine emits structured violations. It does not interpret meaning. This is how Staqtapp-TDS reduces entropy without embedding cognition inside the VFS.

## Numba direction

Rules are declared in Python. Directory facts are compiled into numeric arrays. Fast scans run through NumPy/Numba-compatible records. Python then turns violation codes into readable reports.
