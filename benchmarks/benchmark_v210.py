"""v2.1.0 micro-benchmark harness for EntryIndex, radix, and text chunking.

Run from the repository root after installing in editable mode:
    python benchmarks/benchmark_v210.py

The harness is intentionally dependency-light and prints JSON so results can be
stored over time and compared as the native radix / Swiss-table work deepens.
"""
from __future__ import annotations

import json
import statistics
import string
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle, islice

from staqtapp_tds import EntryIndex, RadixDirectoryRouter, TDSFileSystem


def timed(fn, repeats: int = 5):
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - t0)
    return {"min_s": min(samples), "median_s": statistics.median(samples), "max_s": max(samples)}


def bench_entry_index(backend: str, n: int = 50_000, threads: int = 8):
    idx = EntryIndex(backend=backend)
    keys = [f"key-{i:08d}" for i in range(n)]
    for i, k in enumerate(keys):
        idx.put(k, i)

    def single_lookup():
        for k in keys:
            idx.get_handle(k)

    def batch_lookup():
        idx.get_handles(keys)

    def threaded_lookup():
        def worker(offset: int):
            local = list(islice(cycle(keys[offset::threads] or keys), n // threads))
            for k in local:
                idx.get_handle(k)
        with ThreadPoolExecutor(max_workers=threads) as ex:
            list(ex.map(worker, range(threads)))

    return {
        "backend": idx.backend_name,
        "n": n,
        "threads": threads,
        "single_lookup": timed(single_lookup),
        "batch_lookup": timed(batch_lookup),
        "threaded_lookup": timed(threaded_lookup),
        "stats": getattr(idx.stats(), "__dict__", str(idx.stats())),
    }


def bench_radix(n: int = 25_000):
    r = RadixDirectoryRouter[int]()
    alphabet = string.ascii_lowercase
    keys = ["/".join(["models", alphabet[i % 26] * 4, f"node-{i:08d}"]) for i in range(n)]

    def insert_all():
        rr = RadixDirectoryRouter[int]()
        for i, k in enumerate(keys):
            rr.insert(k, i)

    for i, k in enumerate(keys):
        r.insert(k, i)

    def lookup_all():
        for k in keys:
            r.get(k)

    return {"n": n, "insert": timed(insert_all), "lookup": timed(lookup_all), "stats": r.stats()}


def bench_text_chunks(byte_sizes=(4096, 16_384, 65_536, 262_144)):
    fs = TDSFileSystem("root")
    d = fs.makedirs("/chunks")
    text = ("ascii line\n" * 1000) + ("emoji 😀 café 𝄞\n" * 1000)
    out = {}
    for size in byte_sizes:
        def write_once():
            name = f"text-{size}.txt"
            d.write_text_chunked(name, text, chunk_size=size, overwrite=True)
            d.read_text(name)
        out[str(size)] = timed(write_once)
    return out


if __name__ == "__main__":
    result = {"entry_index": [], "radix": bench_radix(), "text_chunks": bench_text_chunks()}
    for backend in ("python", "auto"):
        try:
            result["entry_index"].append(bench_entry_index(backend))
        except Exception as exc:
            result["entry_index"].append({"backend": backend, "error": repr(exc)})
    print(json.dumps(result, indent=2, sort_keys=True))
