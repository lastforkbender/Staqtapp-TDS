# 19 — Provenance and Cluster Identity

v1.8.0 adds lightweight provenance tags and a minimal cluster identity object.

## Provenance

TDS can now label entries as:

- `UNKNOWN`
- `REAL`
- `SYNTHETIC`
- `DERIVED`
- `SPECULATIVE`
- `MIXED`

This is descriptive only. TDS does not decide truth or reasoning value.

```python
dir.write_text("note.txt", "observed", provenance="REAL")
dir.write("sample", {"x": 1}, provenance=ProvenanceTag.create("SYNTHETIC", source_id="gen-a"))
```

A compact NumPy provenance record is available for future Numba scans.

## Cluster identity

`TDSClusterIdentity` gives thousands of related `.tds` files one governing identity without making cluster search heavy yet.

```python
cluster = TDSClusterIdentity("cluster_alpha")
cluster.add_shard("shards/shard_000001.tds")
feedback = cluster.feedback(entry_count=1000, provenance_counts={"REAL": 600})
```

Cluster query guards require at least one selector unless explicit scanning is enabled. This prevents accidental full-cluster scans.
