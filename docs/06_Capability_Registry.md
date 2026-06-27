# 06 — Capability Registry

The capability registry lets zones advertise which features they support.

Capabilities include:

- `srz`,
- `latency`,
- `telemetry`,
- `compression`,
- `shared_arena`,
- `native_index_ready`,
- `manifest_bound`,
- `reserved_namespaces`.

Clients should ask for capabilities instead of guessing behavior.

```python
caps = fs.capability_snapshot()
print(caps["/root/tokenizers"])
```
