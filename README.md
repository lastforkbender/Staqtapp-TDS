<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=185&text=Staqtapp-TDS%20v1.7&fontAlign=50&fontAlignY=35&desc=Python-first%20VFS%20%7C%20Native-ready%20EntryIndex%20%7C%20Arena%20Handles&descAlign=50&descAlignY=58&color=gradient" alt="Staqtapp-TDS v1.7 banner" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Staqtapp--TDS-v1.7.3-7c3aed?style=for-the-badge" alt="version" />
  <img src="https://img.shields.io/badge/src--layout-clean%20repo-00bcd4?style=for-the-badge" alt="src layout" />
  <img src="https://img.shields.io/badge/EntryIndex-backend%20facade-ff6b00?style=for-the-badge" alt="entry index facade" />
  <img src="https://img.shields.io/badge/Python--first-native%20ready-14b8a6?style=for-the-badge" alt="python first native ready" />
</p>

# Staqtapp-TDS — Temporal Directory System

**Staqtapp-TDS v1.7.3** is a Python-first VFS package with a cleaner repo structure and a formal native-extension seam for the future high-throughput EntryIndex.

This release does **not** force C/C++ on the project. It keeps Python as the main implementation while separating the hot index boundary so native backends can be added later without rewriting the VFS.

## What Staqtapp-TDS is

Staqtapp-TDS is not trying to be an AI. It is the VFS substrate below an AI or agent system. It provides:

- named Python variable storage,
- text/source file storage,
- special variable controls such as `lockvar()` and `stalkvar()`,
- semantic routing metadata,
- directory telemetry,
- persistence to `.tds` files,
- structured status feedback instead of normal operational crashes.

## New in v1.7.3

- Serializer policy module: `serializers.py`.
- Optional fast JSON backend path: `orjson` for dumps, `simdjson` for loads when installed.
- Automatic variable payload kind selection:
  - JSON-safe variables → `JSON_UTF8`
  - NumPy arrays → `NUMPY_ARRAY`
  - complex Python objects → `PICKLE_OBJ`
- Content hashes and size metadata for entries.
- Compression policy with threshold support.
- Whole UTF-8 text storage plus chunked text groundwork.
- Numba/NumPy-friendly `InvariantEngine`.
- Invariant feedback for lock/stalk table disorder, entry limits, and latency hard-limit violations.
- Tests expanded to cover variable payload kinds, text metadata, chunked text, persistence, and invariant failures.

## Variable API

```python
from staqtapp_tds import TDSFileSystem

fs = TDSFileSystem("root")
vars_dir = fs.makedirs("/vars")

vars_dir.addvar("state", {"a": 1})
vars_dir.editvar("state", {"a": 2})
vars_dir.lockvar("state")
vars_dir.unlockvar("state")

vars_dir.stalkvar("~state", {"b": 3})
vars_dir.stalkvar("~state", {"c": 4})
vars_dir.stalkvar("state", None)  # clears state_0001/state_0002, keeps state
```

Normal conflicts return `TDSResult` instead of halting execution.

## Text storage

```python
src = fs.makedirs("/source")
src.write_text("notes.md", "alpha\nbeta")
src.write_text_chunked("large.md", very_large_text, chunk_size=65536)
```

Text is stored as UTF-8, not pickle. Chunked text stores a JSON manifest under the visible file name and hidden UTF-8 chunks under reserved internal chunk names.

## Payload kinds

```text
JSON_UTF8     JSON-safe Python variables and JSON entries
TEXT_UTF8     whole text/source files
NUMPY_ARRAY   NumPy arrays via np.save(..., allow_pickle=False)
PICKLE_OBJ    complex Python variable types that need Python fidelity
```

Pickle remains because Staqtapp is Python-variable-native, but v1.7.3 avoids pickle where a safer first-class lane is suitable.

## Invariant Engine

The Invariant Engine is deterministic verification, not reasoning.

It checks:

- lock variables point to real variables,
- stalk base variables exist,
- latest stalk pointers exist,
- tracked stalk chains are complete,
- `latest_index` matches chain length,
- optional entry count limits,
- latency hard-limit violations.

```python
from staqtapp_tds import InvariantEngine

report = InvariantEngine().evaluate_directory(vars_dir)
print(report.ok)
print(report.as_dict())
```

## Architecture boundary

`EntryIndex` remains clean:

```text
EntryIndex:
  name -> handle/entry

Serializer policy:
  above EntryIndex

Variable semantics:
  above EntryIndex

Invariant checks:
  scan directory/control-table facts
```

The future C/native backend should not know about `stalkvar()`, text chunks, JSON, or pickle. It should only accelerate the index/handle mechanics.

## Install / test

```bash
pip install -e .
pytest -q
```

Expected for this release: **25 tests passed**.

## Roadmap

- **v1.7.x** — stabilize variable and storage semantics.
- **v1.8** — optional native `EntryIndex` backend.
- **v1.9** — broader invariant engine and benchmark suite.
- **v2.0** — mature Python API + optional native hot path.
