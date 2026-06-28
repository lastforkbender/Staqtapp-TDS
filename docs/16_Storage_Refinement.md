# 16 — Storage Refinement

v1.7.3 separates variable storage policy from the EntryIndex seam.

## Payload lanes

- `JSON_UTF8` for JSON-safe Python variables.
- `TEXT_UTF8` for whole text/source files.
- `NUMPY_ARRAY` for NumPy arrays.
- `PICKLE_OBJ` for Python objects that need Python-specific fidelity.

Pickle remains available because Staqtapp is Python-variable-native, but it is no longer the only practical lane.

## JSON backend policy

JSON writing uses `orjson` when installed and Python `json` otherwise. JSON reading uses `simdjson` when installed and Python `json` otherwise. Both accelerators are optional.

## Compression policy

Compression is controlled by policy and thresholds. Small source text is kept raw; larger text can be compressed using the configured codec.

## EntryIndex boundary

The EntryIndex remains name/handle oriented. Serialization details stay above the index so the future C backend does not know about Python variables, text files, or serializer policy.
