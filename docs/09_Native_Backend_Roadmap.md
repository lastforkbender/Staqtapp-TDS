# 09 — Native Backend Roadmap

Native code should enter only through stable seams.

Target first native component:

```text
EntryIndex
    put(bytes, handle)
    get(bytes) -> handle
    delete(bytes)
    contains(bytes)
```

The Python API should not change. Native acceleration should be optional.

Likely v1.8 goal:

- optional pybind11 or Cython backend,
- Python fallback preserved,
- native read path can release the GIL,
- map stores handle values rather than Python objects where possible.
