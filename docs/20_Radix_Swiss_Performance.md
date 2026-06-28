# Radix + Swiss-table Performance Layer

v2.0.1 adds two speed-oriented routing layers with different responsibilities.

## Radix router

The radix router is for directory path structure:

```text
/path/to/deep/semantic/zone
```

It compresses repeated prefixes and provides a clean seam for future native path routing.

It is still Python-side in v2.0.1. That keeps risk low while moving TDS away from direct raw-dict child routing.

## Swiss-table-inspired EntryIndex

The native EntryIndex is for key-to-handle lookup:

```text
name_hash / key_bytes -> int64 handle
```

It uses:

- open addressing,
- control-byte fingerprints,
- triangular probing,
- tombstones,
- native read/write lock,
- GIL-released read lookup.

This is not a full Abseil SwissTable clone. It is a conservative C backend that borrows the important locality/fingerprint idea while preserving safety and testability.

## GIL boundary

GIL released:

```text
NativeHandleIndex.get_handle()
NativeHandleIndex.contains()
```

GIL not released:

```text
Python value lookup by handle
pickle/json/text/compression
manifest parsing
stalkvar/lockvar logic
persistence orchestration
```

## Why both layers exist

```text
Radix solves path shape.
Swiss solves entry lookup.
```

They should remain separate. Combining them would increase architectural entropy and make future native work harder to verify.
