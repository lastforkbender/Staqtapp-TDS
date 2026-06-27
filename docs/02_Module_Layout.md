# 02 — Module Layout

```text
src/staqtapp_tds/
├── tds_filesystem.py      # public VFS behavior
├── tds_persistence.py     # .tds read/write/flush/load
├── arena.py               # handle-oriented byte arena
├── index.py               # EntryIndex facade
├── manifest.py            # read-once manifest policy
├── srz.py                 # Semantic Routing Zone metadata
├── telemetry.py           # directory timing counters/traces
├── latency.py             # latency buckets and policies
├── capabilities.py        # feature capability flags
├── namespaces.py          # reserved namespace support
└── backends/
    ├── python_index.py    # default Python backend
    └── native.py          # future native seam
```

The important rule is separation of responsibility. `tds_filesystem.py` orchestrates features, but SRZ, telemetry, manifest, and capability logic live in separate modules.
