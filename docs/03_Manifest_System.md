# 03 — Manifest System

The `.tds_manifest` is the folder-level authority. It defines policy once, then the runtime uses compiled Python objects.

## Goals

- strict schema/version identity,
- inheritance across directory trees,
- cold-path parsing only,
- manifest hash for file-side validation,
- optional feature advertisement.

## Example

```json
{
  "tds_manifest_version": 1,
  "folder_signature": "STAQTTDS-SRZ-v1",
  "schema_version": "1.7.3",
  "route_stamp_version": "RSPEC-1",
  "hash_policy": "sha256",
  "codec_policy": "raw-or-zlib",
  "strict_mode": true,
  "inherits": true,
  "telemetry": {"mode": "light", "flush_policy": "snapshot", "trace_window": 1024},
  "latency": {"expected_lookup_ns": 50000, "soft_limit_ns": 100000, "hard_limit_ns": 1000000},
  "capabilities": ["srz", "latency", "telemetry", "manifest_bound"],
  "reserved_namespaces": {"directory_names": ["future_zone"], "aliases": [], "route_ids": []}
}
```

## Inheritance

If a folder has no local manifest, parent folders are searched. This reduces duplication and allows a large tree to share one semantic/storage policy.

## What not to put in the manifest

Do not put fast-changing telemetry or cognitive interpretations into the manifest. The manifest is law, not execution.
