<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=185&text=Staqtapp-TDS%20v1.7&fontAlign=50&fontAlignY=35&desc=Python-first%20VFS%20%7C%20Native-ready%20EntryIndex%20%7C%20Arena%20Handles&descAlign=50&descAlignY=58&color=gradient" alt="Staqtapp-TDS v1.7 banner" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Staqtapp--TDS-v1.7.1-7c3aed?style=for-the-badge" alt="version" />
  <img src="https://img.shields.io/badge/src--layout-clean%20repo-00bcd4?style=for-the-badge" alt="src layout" />
  <img src="https://img.shields.io/badge/EntryIndex-backend%20facade-ff6b00?style=for-the-badge" alt="entry index facade" />
  <img src="https://img.shields.io/badge/Python--first-native%20ready-14b8a6?style=for-the-badge" alt="python first native ready" />
</p>

# Staqtapp-TDS — Temporal Directory System

**Staqtapp-TDS v1.7.1** is a Python-first VFS package with a cleaner repo structure and a formal native-extension seam for the future high-throughput EntryIndex.

This release does **not** force C/C++ on the project. It keeps Python as the main implementation while separating the hot index boundary so native backends can be added later without rewriting the VFS.

## What this project is

Staqtapp-TDS is a virtual filesystem layer for storing and retrieving structured data through a stable Python API. It is designed around:

- directory-oriented data zones,
- `.tds` persistence files,
- handle-ready entry indexing,
- optional Semantic Routing Zones (SRZ),
- lightweight directory telemetry,
- read-once manifest policy,
- future optional native/C/C++ backend seams.

## What this project is not

Staqtapp-TDS does **not** perform AI reasoning. It does not interpret cognition, confidence, planning quality, or semantic importance. It exposes facts about storage, routing identity, timing, and capabilities. The consuming AI system decides what those facts mean.

> **Design boundary:** the VFS provides infrastructure; the AI provides reasoning.

## v1.7.1 focus

v1.7.1 is primarily an engineering documentation and stabilization release.

New in v1.7.1:

- Expanded engineering README.
- Full `docs/` directory.
- Reserved namespace support.
- Reserved namespace tests.
- Version bump to `1.7.1`.
- Existing v1.7 semantic infrastructure preserved.

No native C/C++ backend is required in this release.

## Core architecture

```text
AI / Client Layer
        │
        ▼
Python TDS API
        │
        ▼
TDSFileSystem / TDSDirectory
        │
        ├── EntryIndex facade
        ├── ManifestPolicy
        ├── SRZMetadata
        ├── DirectoryTelemetry
        ├── CapabilityRegistry
        └── ReservedNamespaces
        │
        ▼
Persistence Layer (.tds files + .tds.meta files)
```

## Repository layout

```text
staqtapp_tds_v1_7_1/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── docs/
│   ├── 01_Architecture.md
│   ├── 02_Module_Layout.md
│   ├── 03_Manifest_System.md
│   ├── 04_Semantic_Routing_Zones.md
│   ├── 05_Directory_Telemetry.md
│   ├── 06_Capability_Registry.md
│   ├── 07_Concurrency.md
│   ├── 08_Numba_Strategy.md
│   ├── 09_Native_Backend_Roadmap.md
│   ├── 10_Performance_Guide.md
│   ├── 11_Design_Principles.md
│   ├── 12_Roadmap.md
│   └── 13_Future_ASI_Integration.md
├── examples/
│   └── srz_manifest_example.py
├── src/
│   └── staqtapp_tds/
└── tests/
```

## Quick start

```python
from staqtapp_tds import TDSFileSystem, FmtID, TelemetryMode

fs = TDSFileSystem("root")
zone = fs.root.mkdir(
    "tokenizers",
    srz_enabled=True,
    route_stamp="ML.TOK.ENC.SEM.v1",
    source_tags=["ml", "tokenizer", "encoding"],
    aliases=["semantic-token-map"],
    telemetry_mode=TelemetryMode.LIGHT,
)

zone.write("vocab", {"hello": 1, "world": 2}, fmt_id=FmtID.PICKLE_OBJ)
print(zone.read("vocab"))
print(zone.telemetry_snapshot())
print(zone.capability_names())
```

## Manifest philosophy

The `.tds_manifest` is read once and compiled into policy objects. It is not parsed during normal directory access.

```text
Manifest = cold-path law
Directory/SRZ index = hot-path execution
Telemetry = lightweight operational signal
AI interpretation = external
```

## Semantic Routing Zones

SRZ is optional. A directory can be plain or semantic.

```python
plain = fs.root.mkdir("tmp")
semantic = fs.root.mkdir("models", srz_enabled=True, route_stamp="ML.MODEL.ZONE.v1")
```

SRZ stores route identity and metadata. It does not reason.

## Directory telemetry

Telemetry modes:

- `OFF` — no routine timing records.
- `LIGHT` — counters and rolling timing; default.
- `TRACE` — ring-buffer tracing for profiling/debugging.

The hot path remains lean. Telemetry updates are memory-first and can be snapshot/flushed later.

## Reserved namespaces

v1.7.1 adds reserved namespace support. A manifest can reserve future directory names, aliases, or route IDs. Creation is blocked unless explicitly allowed.

```python
from staqtapp_tds import ManifestPolicy, ReservedNamespaces, TDSFileSystem

reserved = ReservedNamespaces(directory_names=("future_zone",))
policy = ManifestPolicy.from_dict({"reserved_namespaces": reserved.to_dict()})
fs = TDSFileSystem("root", manifest_policy=policy)

# fs.root.mkdir("future_zone")  # raises ValueError
fs.root.mkdir("future_zone", allow_reserved=True)
```

Reserved namespaces are a stability mechanism, not prediction. They protect future expansion without giving the VFS responsibility for semantic forecasting.

## Persistence

`TDSPersistence` writes `.tds` files and metadata sidecars. v1.7 stores SRZ, telemetry, capabilities, and reserved namespace metadata in `.tds.meta` sidecars.

```python
from staqtapp_tds import TDSPersistence

p = TDSPersistence("./mount")
p.flush(fs)
loaded = p.load_node("./mount/root__tokenizers.tds")
```

## Testing

```bash
PYTHONPATH=src pytest -q
```

Expected for v1.7.1:

```text
12 passed
```

## Roadmap

- **v1.7.1** — documentation/specification release plus reserved namespaces.
- **v1.8** — optional native `EntryIndex` preview.
- **v1.9** — optional native SRZ/telemetry structures.
- **v2.0** — measured performance release with mature test/benchmark coverage.

## Design principle

> Staqtapp-TDS stores structure, integrity, observability, and speed. It intentionally does not store intelligence.
