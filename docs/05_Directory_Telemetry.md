# 05 — Directory Telemetry

Directory telemetry measures VFS health and access behavior.

Modes:

- `OFF` — no ordinary timing records.
- `LIGHT` — hit/miss counters, last/average/max latency, cold count.
- `TRACE` — ring-buffer access records for debugging.

## Timing formats

Internally, Staqtapp-TDS uses absolute nanoseconds. Reporting can expose ratio and bucket forms.

```text
absolute_ns -> stored internally
ratio       -> actual / expected
bucket      -> hot, warm, cold, slow, timeout
percentile  -> future diagnostic/benchmark layer
```

Telemetry does not judge reasoning quality. It records what happened.
