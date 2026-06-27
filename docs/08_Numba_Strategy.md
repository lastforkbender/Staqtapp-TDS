# 08 — Numba Strategy

Numba is useful where data is already numeric and array-shaped.

Good Numba candidates:

- registry scoring,
- score decay,
- packed slot metadata,
- Bloom filter bit manipulation,
- future SRZ/telemetry compact arrays.

Poor Numba candidates:

- Python object graphs,
- dictionary-heavy logic,
- high-level directory orchestration,
- manifest parsing.

The long-term strategy is to make hot metadata NumPy-structured where practical, then JIT small kernels around those arrays.
