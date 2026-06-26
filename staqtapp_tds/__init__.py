"""
Staqtapp-TDS — Temporal Directory System
VFS for ASI-scale computation. v1.2.0

Changes from v1.1.188:
  BUGS FIXED
  - _LazyEntry key mismatch: reads after load_node no longer KeyError
  - _LazyEntry.serialise double-wrap: re-flush round-trips no longer corrupt
  - HybridRegistry eviction now score-based (was FIFO)
  - ConcurrencyPool._ensure_loop now thread-safe
  - ProcessPoolExecutor dead code + OS handle leak removed
  - parallel_read_all deadlock path eliminated
  - TDSWriter recursive walk snapshots children under lock
  - SlotIndex lookup is now O(1) dict (was O(n) linear fallback)
  - TDSReader.reload() added for post-shadow-swap inode refresh

  NEW FEATURES
  - BloomFilter: zero-seek definite-miss path on every read
  - CompressorRegistry: pluggable codecs (zlib default; lz4/zstd if installed)
  - EntrySchema: per-entry dtype + shape + type validation
  - async surface: TDSDirectory.aread() / awrite()
  - WriteAheadLog: append + checkpoint + replay for crash recovery
  - _join_segments now preserves caller-specified dtype
"""

from staqtapp_tds.tds_filesystem import (
    TDSFileSystem,
    TDSDirectory,
    TDSEntry,
    FmtID,
    DirFlags,
    HybridRegistry,
    LoopCacheManager,
    LoopCacheSlot,
    ConcurrencyPool,
    SymbolTable,
    BloomFilter,
    CompressorRegistry,
    EntrySchema,
    WriteAheadLog,
    encode_header,
    decode_header,
    HEADER_SIZE,
    TDS_MAGIC,
)

from staqtapp_tds.tds_persistence import (
    TDSReader,
    TDSWriter,
    TDSPersistence,
    ParallelFlusher,
    SlotIndex,
    SlotRecord,
    FILE_HDR_SIZE,
    FILE_MAGIC,
)

__version__ = "1.2.0"
__all__ = [
    # filesystem
    "TDSFileSystem", "TDSDirectory", "TDSEntry",
    "FmtID", "DirFlags",
    "HybridRegistry", "LoopCacheManager", "LoopCacheSlot",
    "ConcurrencyPool", "SymbolTable",
    "BloomFilter", "CompressorRegistry", "EntrySchema", "WriteAheadLog",
    "encode_header", "decode_header",
    "HEADER_SIZE", "TDS_MAGIC",
    # persistence
    "TDSReader", "TDSWriter", "TDSPersistence", "ParallelFlusher",
    "SlotIndex", "SlotRecord",
    "FILE_HDR_SIZE", "FILE_MAGIC",
]
