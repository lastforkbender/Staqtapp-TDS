# Staqtapp-TDS — Temporal Directory System

> **A virtual file system engineered for ASI-scale computation.**
> Binary-native. Math-accelerated. Concurrency-first. No CSV. No comma crap.
> Updated to v1.1.188, several issues fixed.

## Install

```bash
pip install staqtapp-tds          # numpy only (pure-Python fallback kernels)
pip install staqtapp-tds[fast]    # + Numba JIT for full performance
```

## Quick Start

```python
from staqtapp_tds import TDSFileSystem, FmtID, DirFlags
from staqtapp_tds import TDSPersistence, TDSReader
import numpy as np

fs     = TDSFileSystem("asi_root")
vec_db = fs.makedirs("databases/vectors",
                      fmt_id=FmtID.NUMPY_MATRIX,
                      flags=DirFlags.PARALLEL_IO | DirFlags.PROB_SORT)

for i in range(100):
    mat = np.random.randn(512, 512).astype(np.float32)
    vec_db.write(f"embed_{i:04d}", mat, fmt_id=FmtID.NUMPY_MATRIX, compress=True)

persist = TDSPersistence("/var/tds/asi")
persist.mount(fs)
persist.flush(fs, parallel_nodes=True)
persist.unmount()

with TDSReader("/var/tds/asi/asi_root__databases__vectors.tds") as r:
    mat = r.read("embed_0042")
    all_embeds = r.read_many(r.keys())
```

---

## New Features added 2026

(1) BloomFilter: zero-seek definite miss path on every read
(2) CompressorRegistry: pluggable codecs (zlib default; lz4/zstd if installed)
(3) EntrySchema: per-entry dtype + shape + type validation
(4) Async surface: TDSDirectory.aread() / awrite()
(5) WriteAheadLog: append + checkpoint + replay for crash recovery
(6) _join_segments now preserves caller-specified dtype

---

## Table of Contents

1. [Overview](#overview)
2. [Why Not Existing File Systems?](#why-not-existing-file-systems)
3. [Architecture at a Glance](#architecture-at-a-glance)
4. [Module Map](#module-map)
5. [Binary Format Reference](#binary-format-reference)
6. [Read Path — Three Tiers](#read-path--three-tiers)
7. [Write Path — Atomic Shadow Swap](#write-path--atomic-shadow-swap)
8. [Core Subsystems](#core-subsystems)
9. [Numba JIT Kernels](#numba-jit-kernels)
10. [Concurrency Model](#concurrency-model)
11. [API Reference Summary](#api-reference-summary)
12. [Performance Characteristics](#performance-characteristics)
13. [Dependency Matrix](#dependency-matrix)
14. [Roadmap](#roadmap)

---

## Overview

`.tds` (Temporal Directory System) is a virtual file system built ground-up for the data demands of Artificial Superintelligence — vast, multi-dimensional, mathematically dense, and in constant parallel flux. Where conventional file systems store blobs named by strings and rely on OS-level structures, TDS treats the directory itself as a first-class mathematical object: binary-encoded, CRC-verified, probability-sorted, and concurrency-pooled from the moment it is instantiated.

Every design decision answers the same question: **what does a file system look like when the entity using it processes more information per second than all human libraries combined?**

---

## Why Not Existing File Systems?

| Concern | ext4 / NTFS / APFS | JSON / CSV stores | **TDS** |
|---|---|---|---|
| Header format | Kernel-managed inode (opaque) | Plain text — bytes wasted on commas, quotes, keys | 36-byte binary struct, CRC-verified |
| Timestamp precision | Seconds or milliseconds | String — parsed per read | Nanosecond `uint64`, embedded in header |
| Directory lookup | Hash table (kernel) | Full parse required | Numba O(log n) binary search over sorted hash array |
| Concurrency | File locks, kernel scheduler | None | Guaranteed `ConcurrencyPool` singleton |
| Variable type awareness | None | Fragile schema conventions | `FmtID` OR-flag in header |
| Probability-based access ordering | None | None | `HybridRegistry`: decay-weighted LRU |
| Pinned cycle variables | Not a concept | Not a concept | `LoopCacheManager` |
| Matrix symbol switching | Not a concept | Not a concept | `SymbolTable` + Numba kernel |
| Atomic writes | Manual | Not atomic | Shadow-file + `fsync` + `os.rename` |
| Lazy disk reads | Not a concept | Not a concept | `_LazyEntry`: mmap placeholder |
| Parallel flush | Not a concept | Not a concept | `ParallelFlusher` |

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                        TDSFileSystem                            │
│   root TDSDirectory                                             │
│   ├── makedirs / resolve / parallel_batch_write                 │
│   └── snapshot_headers                                          │
└───────────────────────┬─────────────────────────────────────────┘
                        │ owns tree of
┌───────────────────────▼─────────────────────────────────────────┐
│                      TDSDirectory                               │
│  Binary Header (36B, CRC32)  │  HybridRegistry (prob-LRU)      │
│  LoopCacheManager            │  SymbolTable                     │
│  TDSEntry dict               │  ConcurrencyPool hook            │
└───────────────────────┬─────────────────────────────────────────┘
                        │ persisted by
┌───────────────────────▼─────────────────────────────────────────┐
│                    TDSPersistence                               │
│  TDSWriter (shadow swap)  │  TDSReader (mmap)                   │
│  SlotIndex (Numba seek)   │  ParallelFlusher                    │
└───────────────────────┬─────────────────────────────────────────┘
                        │ accelerated by
┌───────────────────────▼─────────────────────────────────────────┐
│                    Numba JIT Kernels                            │
│  _compute_subdir_offsets  │  _probability_decay                 │
│  _matrix_symbol_swap      │  _slot_binary_search                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Map

| File | Section | Responsibility |
|---|---|---|
| `tds_filesystem.py` | §1 | Binary header encode / decode |
| `tds_filesystem.py` | §2 | Numba JIT math kernels |
| `tds_filesystem.py` | §3 | `HybridRegistry` — probability-LRU |
| `tds_filesystem.py` | §4 | `LoopCacheManager` — pinned cycle vars |
| `tds_filesystem.py` | §5 | `ConcurrencyPool` — guaranteed singleton |
| `tds_filesystem.py` | §6 | `SymbolTable` — bi-directional sym ↔ id |
| `tds_filesystem.py` | §7 | `TDSEntry` — leaf variable storage |
| `tds_filesystem.py` | §8 | `TDSDirectory` — core tree node |
| `tds_filesystem.py` | §9 | `TDSFileSystem` — root mount API |
| `tds_persistence.py` | §10 | File-level constants and struct formats |
| `tds_persistence.py` | §11 | `SlotIndex` + `SlotRecord` — seek table |
| `tds_persistence.py` | §12 | `TDSReader` — mmap random-access reader |
| `tds_persistence.py` | §13 | `TDSWriter` — atomic shadow-swap writer |
| `tds_persistence.py` | §14 | `TDSPersistence` — mount / flush / load |
| `tds_persistence.py` | §14b | `_LazyEntry` — deferred mmap read |
| `tds_persistence.py` | §15 | `ParallelFlusher` — concurrent node flush |

---

## Binary Format Reference

### In-Memory Directory Header (36 bytes)

```
Offset  Size  Type     Field
──────  ────  ───────  ──────────────────────────────────────
0       4     bytes    Magic: 0x54 44 53 01  ("TDS\x01")
4       8     uint64   ts_create — nanosecond creation timestamp
12      8     uint64   ts_mod    — nanosecond last-modified timestamp
20      2     uint16   flags     — DirFlags bit field
22      2     uint16   fmt_id    — FmtID of stored data
24      4     uint32   subdir_count
28      4     uint32   entry_count
32      4     uint32   CRC32 of bytes 0–31
──────  ────  ───────  ──────────────────────────────────────
        36             Total
```

### On-Disk File Header (44 bytes)

```
Offset  Size  Type     Field
──────  ────  ───────  ──────────────────────────────────────
0       4     bytes    Magic: 0x54 44 53 58  ("TDSX")
4       4     uint32   Format version        (currently 1)
8       8     uint64   slot_count
16      8     uint64   index_offset
24      8     uint64   data_offset
32      8     uint64   Timestamp (ns)
40      4     uint32   CRC32 of bytes 0–39
──────  ────  ───────  ──────────────────────────────────────
        44             Total
```

### FmtID Encoding

| Name | Value | Description |
|---|---|---|
| `RAW_BINARY` | `0x00` | Untyped byte buffer |
| `NUMPY_MATRIX` | `0x01` | NumPy array via `np.save` |
| `PICKLE_OBJ` | `0x02` | Arbitrary Python object, protocol 5 |
| `SYMBOL_TABLE` | `0x04` | Pickled symbol table dict |
| `LOOP_CACHE` | `0x08` | Pickled loop-cache slot state |
| `COMPRESSED` | `0x80` | OR-able modifier — zlib |

### DirFlags Bit Field

| Name | Hex | Effect |
|---|---|---|
| `NONE` | `0x0000` | No special behaviour |
| `READONLY` | `0x0001` | Reject write operations |
| `ENCRYPTED` | `0x0002` | Reserved |
| `PARALLEL_IO` | `0x0004` | Sub-directory reads fan out across pool |
| `LOOP_PINNED` | `0x0008` | Loop-cache slots held in memory |
| `RECURSIVE` | `0x0010` | Enable recursive array join traversal |
| `PROB_SORT` | `0x0020` | `ls()` returns probability-sorted order |

---

## Read Path — Three Tiers

| Tier | Location | Mechanism | Cost |
|---|---|---|---|
| **1 — Registry Hot Path** | RAM — `HybridRegistry` | `OrderedDict` lookup | O(1) |
| **2 — Directory Node** | RAM — `TDSDirectory._entries` | Direct dict lookup | O(1) + decompression |
| **3 — Lazy mmap** | Disk — `.tds` file | `SlotIndex.lookup()` → mmap slice | O(log n) + I/O |

---

## Write Path — Atomic Shadow Swap

1. Serialise all entries (parallel threads)
2. Build `SlotIndex` — one `SlotRecord` per entry
3. Open shadow file `<name>.tds~`
4. Write header + data block + index block
5. `f.flush()` → `os.fsync(fd)`
6. `shutil.move(".tds~" → ".tds")` — atomic POSIX rename

Readers never observe a partial file.

---

## Core Subsystems

### HybridRegistry — Probability-LRU

Decay-weighted LRU cache. Score formula:

```
score(i) = access_count(i) × e^(−λ × Δt)
```

where `λ = 1e-4`. Capacity: 4096 entries per node. Thread-safe via `RLock`.

### SlotIndex — Numba Binary Search

Sorted `int64` hash array + argsort index. Lookup: `Adler-32(name)` → Numba O(log n) binary search → mmap offset. No string comparison in the hot path.

### LoopCacheManager — Pinned Cycle Variables

Named slots with configurable `cycle`. `write()` returns `True` every `cycle`-th call — signalling a stable value boundary.

### ConcurrencyPool — Guaranteed Hook

Singleton. 64 thread workers + 8 process workers + 1 asyncio daemon loop. Every `TDSDirectory` acquires it at construction — zero configuration.

### SymbolTable — Matrix-Level Switching

Bidirectional `symbol ↔ float64 ID`. `swap(old, new, matrix)` calls the Numba `_matrix_symbol_swap` kernel — instant in-place substitution across the entire matrix.

---

## Numba JIT Kernels

All use `@njit(cache=True)`. Pure-Python shim provided for Numba-free environments.

| Kernel | Complexity | Purpose |
|---|---|---|
| `_compute_subdir_offsets` | O(n) | Prefix-sum seek offsets |
| `_probability_decay` | O(n) parallel | Decay-weighted registry scores |
| `_matrix_symbol_swap` | O(n²) parallel | In-place symbol substitution |
| `_slot_binary_search` | O(log n) | Seek-table lookup |
| `_build_sorted_order` | O(n log n) | SlotIndex argsort |

---

## Concurrency Model

```
ConcurrencyPool (singleton)
├── ThreadPoolExecutor  (64 workers)  — I/O, registry, flush nodes
├── ProcessPoolExecutor (8 workers)   — CPU-bound compression
└── asyncio event loop  (daemon)      — async coroutine support
```

All mmap reads are `ACCESS_READ` — unlimited concurrent readers, zero cross-node contention on parallel flush.

---

## API Reference Summary

### `TDSFileSystem`
| Method | Returns | Description |
|---|---|---|
| `makedirs(path, **kwargs)` | `TDSDirectory` | mkdir -p style creation |
| `resolve(path)` | `TDSDirectory` | Walk path string → node |
| `parallel_batch_write(writes)` | `None` | Fan out `[(path, name, value)]` writes |
| `snapshot_headers()` | `Dict[str, dict]` | Decode headers of every node |

### `TDSDirectory`
| Method | Returns | Description |
|---|---|---|
| `write(name, value, fmt_id, compress)` | `TDSEntry` | Store a variable |
| `read(name)` | `Any` | Retrieve (3-tier path) |
| `delete(name)` | `None` | Remove an entry |
| `mkdir(name, **kwargs)` | `TDSDirectory` | Create sub-directory |
| `ls(sort_by_prob)` | `List[str]` | List contents |
| `parallel_read_all()` | `Dict[str, Any]` | Read all entries via pool |
| `recursive_join(dtype, max_depth)` | `np.ndarray` | Concat all numpy arrays in subtree |

### `TDSReader`
| Method | Returns | Description |
|---|---|---|
| `read(name)` | `Any` | O(log n) seek + deserialise |
| `read_many(names)` | `Dict[str, Any]` | Parallel mmap reads |
| `keys()` | `List[str]` | All entry names |
| `close()` | `None` | Release mmap and fd |

### `TDSPersistence`
| Method | Returns | Description |
|---|---|---|
| `mount(fs)` | `None` | Attach FS |
| `flush(fs, parallel_nodes)` | `Dict[str, int]` | Write all nodes |
| `load_node(path, into)` | `TDSDirectory` | Read `.tds` file → directory (lazy) |
| `unmount()` | `Dict[str, int]` | Flush + close all readers |

---

## Performance Characteristics

| Operation | Complexity |
|---|---|
| `write(name, value)` | O(1) amortised |
| `read(name)` — hot | O(1) |
| `read(name)` — disk | O(log n) + I/O |
| `ls(sort_by_prob=True)` | O(n log n) |
| `flush(fs, parallel=True)` | O(nodes) parallel |
| `SlotIndex.lookup()` | O(log n) Numba |

---

## Dependency Matrix

| Library | Required? |
|---|---|
| `numpy` | **Yes** |
| `numba` | No — shim provided |
| `zlib`, `pickle`, `struct`, `mmap`, `asyncio`, `threading`, `uuid` | **Yes** (all stdlib) |

---

## Roadmap

| Feature | Status |
|---|---|
| Binary directory header | ✅ Complete |
| Numba JIT math kernels | ✅ Complete |
| Probability-LRU registry | ✅ Complete |
| Loop cache manager | ✅ Complete |
| ConcurrencyPool singleton | ✅ Complete |
| Symbol table + matrix swap | ✅ Complete |
| mmap-backed reader | ✅ Complete |
| Atomic shadow-swap writer | ✅ Complete |
| Parallel flush | ✅ Complete |
| Encryption layer (AES-256-GCM) | 🔲 Planned |
| Distributed mount | 🔲 Planned |
| Streaming write mode | 🔲 Planned |
| Typed tensor extension (`FmtID.TENSOR_4D`) | 🔲 Planned |
| WAL (write-ahead log) | 🔲 Planned |

---

*TDS v1.1.188 — Temporal Directory System — built for the age of ASI.*
