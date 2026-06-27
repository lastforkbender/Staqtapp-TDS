# 10 — Performance Guide

Measure before optimizing.

Important benchmarks:

- entry lookup latency,
- registry hit latency,
- registry miss latency,
- directory creation overhead,
- persistence flush throughput,
- load-node speed,
- compressed vs raw payload read time,
- telemetry overhead in OFF/LIGHT/TRACE.

Recommended reporting:

```text
p50 / p95 / p99 latency
throughput ops/sec
memory per directory
memory per entry
contention under N threads
```

Telemetry should be measured as overhead too. If telemetry becomes too expensive, it violates the VFS boundary.
