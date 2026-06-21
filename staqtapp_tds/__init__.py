"""
Staqtapp-TDS — Temporal Directory System
VFS for ASI-scale computation. v1.1.188
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

__version__ = "1.1.188"
__all__ = [
    # filesystem
    "TDSFileSystem", "TDSDirectory", "TDSEntry",
    "FmtID", "DirFlags",
    "HybridRegistry", "LoopCacheManager", "LoopCacheSlot",
    "ConcurrencyPool", "SymbolTable",
    "encode_header", "decode_header",
    "HEADER_SIZE", "TDS_MAGIC",
    # persistence
    "TDSReader", "TDSWriter", "TDSPersistence", "ParallelFlusher",
    "SlotIndex", "SlotRecord",
    "FILE_HDR_SIZE", "FILE_MAGIC",
]
